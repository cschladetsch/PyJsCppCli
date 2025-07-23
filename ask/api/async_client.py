"""Async Claude API client with streaming support"""

import asyncio
import json
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

import aiohttp

from ..constants import DEFAULT_MAX_TOKENS, DEFAULT_MODEL, DEFAULT_SYSTEM_PROMPT
from ..models import Interaction
from ..utils.io import get_api_key


class AsyncClaudeClient:
    """Asynchronous client for Claude API with streaming support"""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        api_key: Optional[str] = None,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.api_key = api_key or get_api_key()
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "anthropic-version": "2023-06-01",
            "x-api-key": self.api_key,
            "content-type": "application/json",
        }

    def _build_messages(
        self, query: str, interactions: Optional[List[Interaction]] = None
    ) -> List[Dict[str, str]]:
        """Build message history for the API"""
        messages = []

        # Add conversation history
        if interactions:
            for interaction in interactions:
                messages.append({"role": "user", "content": interaction.query})
                messages.append({"role": "assistant", "content": interaction.response})

        # Add current query
        messages.append({"role": "user", "content": query})

        return messages

    def _build_request(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        interactions: Optional[List[Interaction]] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Build request payload"""
        return {
            "model": self.model,
            "messages": self._build_messages(query, interactions),
            "system": system_prompt or DEFAULT_SYSTEM_PROMPT,
            "max_tokens": self.max_tokens,
            "stream": stream,
        }

    async def stream_response(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        interactions: Optional[List[Interaction]] = None,
    ) -> AsyncIterator[str]:
        """Stream response chunks as they arrive"""
        if not self.session:
            raise RuntimeError("Client must be used within async context manager")

        payload = self._build_request(query, system_prompt, interactions, stream=True)

        async with self.session.post(
            self.base_url, headers=self._get_headers(), json=payload
        ) as response:
            response.raise_for_status()

            async for line in response.content:
                if line:
                    line_str = line.decode("utf-8").strip()
                    if line_str.startswith("data: "):
                        data_str = line_str[6:]  # Remove "data: " prefix

                        if data_str == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            if data.get("type") == "content_block_delta":
                                delta = data.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    yield delta.get("text", "")
                        except json.JSONDecodeError:
                            continue

    async def complete(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        interactions: Optional[List[Interaction]] = None,
    ) -> Tuple[str, List[Interaction]]:
        """Get complete response (non-streaming)"""
        if not self.session:
            raise RuntimeError("Client must be used within async context manager")

        payload = self._build_request(query, system_prompt, interactions, stream=False)

        async with self.session.post(
            self.base_url, headers=self._get_headers(), json=payload
        ) as response:
            response.raise_for_status()
            data = await response.json()

        # Extract response text
        content = data.get("content", [])
        response_text = ""
        for block in content:
            if block.get("type") == "text":
                response_text += block.get("text", "")

        # Create updated interactions list
        new_interaction = Interaction(
            query=query, response=response_text, timestamp=datetime.now().isoformat()
        )

        updated_interactions = (interactions or []) + [new_interaction]

        return response_text, updated_interactions

    async def complete_with_retry(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        interactions: Optional[List[Interaction]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> Tuple[str, List[Interaction]]:
        """Complete with automatic retry on failure"""
        last_error = None

        for attempt in range(max_retries):
            try:
                return await self.complete(query, system_prompt, interactions)
            except aiohttp.ClientResponseError as e:
                if e.status == 429:  # Rate limit
                    retry_after = float(e.headers.get("Retry-After", retry_delay))
                    await asyncio.sleep(retry_after)
                elif e.status >= 500:  # Server error
                    await asyncio.sleep(retry_delay * (attempt + 1))
                else:
                    raise
                last_error = e
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                await asyncio.sleep(retry_delay * (attempt + 1))
                last_error = e

        raise last_error or Exception("Max retries exceeded")
