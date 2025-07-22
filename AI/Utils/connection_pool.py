"""
Connection pooling utilities for API calls

This module provides connection pooling and session management
for efficient API communication with rate limiting and retry logic.
"""

import asyncio
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import aiohttp

from ..utils.config import get_config
from ..utils.exceptions import APIError, NetworkError, RateLimitError
from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ConnectionStats:
    """Connection pool statistics."""

    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    retry_count: int = 0
    average_response_time: float = 0.0
    last_error: Optional[str] = None
    last_error_time: Optional[float] = None


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""

    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 3600
    max_requests_per_day: int = 50000
    backoff_factor: float = 1.5
    max_backoff_time: float = 300.0  # 5 minutes

    # Track request timestamps
    request_timestamps: List[float] = field(default_factory=list)

    def can_make_request(self) -> bool:
        """Check if we can make a request based on rate limits."""
        current_time = time.time()

        # Clean old timestamps
        self._clean_old_timestamps(current_time)

        # Check minute limit
        minute_ago = current_time - 60
        recent_requests = len([t for t in self.request_timestamps if t > minute_ago])
        if recent_requests >= self.max_requests_per_minute:
            return False

        # Check hour limit
        hour_ago = current_time - 3600
        hour_requests = len([t for t in self.request_timestamps if t > hour_ago])
        if hour_requests >= self.max_requests_per_hour:
            return False

        # Check day limit
        day_ago = current_time - 86400
        day_requests = len([t for t in self.request_timestamps if t > day_ago])
        if day_requests >= self.max_requests_per_day:
            return False

        return True

    def record_request(self) -> None:
        """Record a request timestamp."""
        self.request_timestamps.append(time.time())

    def _clean_old_timestamps(self, current_time: float) -> None:
        """Remove timestamps older than 24 hours."""
        day_ago = current_time - 86400
        self.request_timestamps = [t for t in self.request_timestamps if t > day_ago]

    def get_wait_time(self) -> float:
        """Get the time to wait before next request."""
        if self.can_make_request():
            return 0.0

        current_time = time.time()

        # Check which limit is hit and return appropriate wait time
        minute_ago = current_time - 60
        recent_requests = [t for t in self.request_timestamps if t > minute_ago]

        if len(recent_requests) >= self.max_requests_per_minute:
            # Wait until oldest request in the minute window expires
            return recent_requests[0] + 60 - current_time + 1

        return 60.0  # Default wait time


class ConnectionPool:
    """
    Connection pool for API requests with rate limiting and retry logic.

    This class manages HTTP connections to the API with:
    - Connection pooling for efficiency
    - Rate limiting to respect API limits
    - Automatic retry with exponential backoff
    - Connection health monitoring
    - Request/response logging
    """

    def __init__(
        self,
        max_connections: int = 10,
        max_connections_per_host: int = 5,
        timeout: float = 30.0,
        max_retries: int = 3,
        rate_limit_config: Optional[RateLimitConfig] = None,
    ):
        """
        Initialize connection pool.

        Args:
            max_connections: Maximum total connections
            max_connections_per_host: Maximum connections per host
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            rate_limit_config: Rate limiting configuration
        """
        self.max_connections = max_connections
        self.max_connections_per_host = max_connections_per_host
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit = rate_limit_config or RateLimitConfig()

        self._session: Optional[aiohttp.ClientSession] = None
        self._connector: Optional[aiohttp.TCPConnector] = None
        self._stats = ConnectionStats()
        self._closed = False

        # Create timeout configuration
        self._timeout = aiohttp.ClientTimeout(
            total=timeout, connect=timeout / 3, sock_read=timeout / 3
        )

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def initialize(self) -> None:
        """Initialize the connection pool."""
        if self._session is not None:
            return

        # Create TCP connector with connection limits
        self._connector = aiohttp.TCPConnector(
            limit=self.max_connections,
            limit_per_host=self.max_connections_per_host,
            enable_cleanup_closed=True,
            ttl_dns_cache=300,  # 5 minutes DNS cache
            use_dns_cache=True,
        )

        # Create client session
        self._session = aiohttp.ClientSession(
            connector=self._connector,
            timeout=self._timeout,
            headers={"User-Agent": "Ask-CLI/0.2.1"},
        )

        self._stats.total_connections = self.max_connections
        logger.info(
            f"Connection pool initialized with {self.max_connections} max connections"
        )

    async def close(self) -> None:
        """Close the connection pool."""
        if self._closed:
            return

        if self._session:
            await self._session.close()

        if self._connector:
            await self._connector.close()

        self._closed = True
        logger.info("Connection pool closed")

    async def request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """
        Make an HTTP request with rate limiting and retry logic.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            HTTP response

        Raises:
            NetworkError: If request fails after retries
            RateLimitError: If rate limit is exceeded
            APIError: If API returns an error
        """
        if self._closed:
            raise NetworkError("Connection pool is closed")

        if self._session is None:
            await self.initialize()

        # Check rate limits
        await self._check_rate_limits()

        # Record request
        self.rate_limit.record_request()
        self._stats.total_requests += 1

        # Retry loop
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()

                # Make request
                response = await self._session.request(method, url, **kwargs)

                # Update stats
                response_time = time.time() - start_time
                self._update_response_time(response_time)

                # Check for API errors
                if response.status >= 400:
                    error_text = await response.text()
                    if response.status == 429:
                        # Rate limit error
                        retry_after = response.headers.get("Retry-After")
                        wait_time = int(retry_after) if retry_after else 60
                        raise RateLimitError(
                            f"Rate limit exceeded: {response.status}",
                            retry_after=wait_time,
                        )
                    if response.status >= 500:
                        # Server error - retry
                        raise NetworkError(
                            f"Server error: {response.status} - {error_text}"
                        )
                    # Client error - don't retry
                    raise APIError(
                        f"API error: {response.status} - {error_text}",
                        status_code=response.status,
                    )

                logger.debug(f"Request successful: {method} {url} - {response.status}")
                return response

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                self._stats.failed_requests += 1

                if attempt < self.max_retries:
                    wait_time = self._calculate_backoff_time(attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}"
                    )
                    logger.info(f"Retrying in {wait_time:.1f} seconds...")
                    await asyncio.sleep(wait_time)
                    self._stats.retry_count += 1
                else:
                    logger.error(
                        f"Request failed after {self.max_retries + 1} attempts: {e}"
                    )
                    self._stats.last_error = str(e)
                    self._stats.last_error_time = time.time()
                    raise NetworkError(
                        f"Request failed after {self.max_retries + 1} attempts: {e}"
                    )

        # This should never be reached
        raise NetworkError("Unexpected error in request retry loop")

    async def _check_rate_limits(self) -> None:
        """Check and enforce rate limits."""
        if not self.rate_limit.can_make_request():
            wait_time = self.rate_limit.get_wait_time()
            logger.warning(f"Rate limit reached, waiting {wait_time:.1f} seconds")
            await asyncio.sleep(wait_time)

    def _calculate_backoff_time(self, attempt: int) -> float:
        """Calculate exponential backoff time."""
        base_wait = 1.0 * (self.rate_limit.backoff_factor**attempt)
        return min(base_wait, self.rate_limit.max_backoff_time)

    def _update_response_time(self, response_time: float) -> None:
        """Update average response time."""
        if self._stats.average_response_time == 0:
            self._stats.average_response_time = response_time
        else:
            # Simple moving average
            self._stats.average_response_time = (
                self._stats.average_response_time * 0.9 + response_time * 0.1
            )

    def get_stats(self) -> ConnectionStats:
        """Get connection pool statistics."""
        if self._connector:
            self._stats.active_connections = len(self._connector._conns)
            self._stats.idle_connections = sum(
                len(conns) for conns in self._connector._conns.values()
            )

        return self._stats

    def reset_stats(self) -> None:
        """Reset connection pool statistics."""
        self._stats = ConnectionStats()
        self._stats.total_connections = self.max_connections


class AsyncAPIClient:
    """
    Async API client with connection pooling.

    This class provides a high-level interface for making API requests
    with automatic connection pooling, rate limiting, and error handling.
    """

    def __init__(
        self, base_url: str, api_key: str, pool_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize API client.

        Args:
            base_url: Base URL for API requests
            api_key: API key for authentication
            pool_config: Connection pool configuration
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

        # Create connection pool
        pool_config = pool_config or {}
        self.pool = ConnectionPool(**pool_config)

        # Common headers
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self.pool.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.pool.close()

    async def post(
        self, endpoint: str, data: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """
        Make a POST request.

        Args:
            endpoint: API endpoint
            data: Request data
            **kwargs: Additional request parameters

        Returns:
            Response data
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        headers = self.headers.copy()
        headers.update(kwargs.pop("headers", {}))

        async with self.pool.request(
            "POST", url, json=data, headers=headers, **kwargs
        ) as response:
            return await response.json()

    async def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Make a GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters
            **kwargs: Additional request parameters

        Returns:
            Response data
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        headers = self.headers.copy()
        headers.update(kwargs.pop("headers", {}))

        async with self.pool.request(
            "GET", url, params=params, headers=headers, **kwargs
        ) as response:
            return await response.json()

    async def stream_post(self, endpoint: str, data: Dict[str, Any], **kwargs):
        """
        Make a streaming POST request.

        Args:
            endpoint: API endpoint
            data: Request data
            **kwargs: Additional request parameters

        Yields:
            Response chunks
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        headers = self.headers.copy()
        headers.update(kwargs.pop("headers", {}))

        async with self.pool.request(
            "POST", url, json=data, headers=headers, **kwargs
        ) as response:
            async for chunk in response.content.iter_chunked(8192):
                yield chunk

    def get_pool_stats(self) -> ConnectionStats:
        """Get connection pool statistics."""
        return self.pool.get_stats()


# Global connection pool instance
_global_pool: Optional[ConnectionPool] = None


async def get_global_pool() -> ConnectionPool:
    """Get the global connection pool instance."""
    global _global_pool
    if _global_pool is None:
        config = get_config()
        _global_pool = ConnectionPool(
            max_connections=config.api.max_retries * 2, timeout=config.api.timeout
        )
        await _global_pool.initialize()
    return _global_pool


@asynccontextmanager
async def api_client(base_url: str, api_key: str, **kwargs):
    """
    Context manager for API client with connection pooling.

    Args:
        base_url: Base URL for API requests
        api_key: API key for authentication
        **kwargs: Additional configuration

    Yields:
        AsyncAPIClient instance
    """
    async with AsyncAPIClient(base_url, api_key, **kwargs) as client:
        yield client
