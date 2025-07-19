"""
Streaming response utilities for Ask CLI

This module provides utilities for handling streaming responses from
the API, including real-time display, buffering, and event processing.
"""

import asyncio
import json
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

import aiohttp

from ..utils.exceptions import APIError, NetworkError
from ..utils.logging import get_logger

logger = get_logger(__name__)


class StreamEventType(Enum):
    """Types of streaming events."""

    START = "start"
    CHUNK = "chunk"
    END = "end"
    ERROR = "error"
    METADATA = "metadata"


@dataclass
class StreamEvent:
    """Streaming event data."""

    event_type: StreamEventType
    data: Any
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None


class StreamBuffer:
    """
    Buffer for streaming data with real-time processing.

    This class handles buffering of streaming data and provides
    methods for processing chunks as they arrive.
    """

    def __init__(self, max_size: int = 1024 * 1024):  # 1MB default
        """
        Initialize stream buffer.

        Args:
            max_size: Maximum buffer size in bytes
        """
        self.max_size = max_size
        self.buffer = []
        self.total_size = 0
        self.start_time = time.time()
        self.last_chunk_time = time.time()
        self.chunk_count = 0

    def add_chunk(self, chunk: str) -> None:
        """
        Add a chunk to the buffer.

        Args:
            chunk: Data chunk to add

        Raises:
            ValueError: If buffer would exceed max size
        """
        chunk_size = len(chunk.encode("utf-8"))

        if self.total_size + chunk_size > self.max_size:
            raise ValueError(f"Buffer would exceed max size ({self.max_size} bytes)")

        self.buffer.append(chunk)
        self.total_size += chunk_size
        self.last_chunk_time = time.time()
        self.chunk_count += 1

    def get_content(self) -> str:
        """Get the complete buffered content."""
        return "".join(self.buffer)

    def clear(self) -> None:
        """Clear the buffer."""
        self.buffer.clear()
        self.total_size = 0
        self.chunk_count = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics."""
        current_time = time.time()
        duration = current_time - self.start_time

        return {
            "total_size": self.total_size,
            "chunk_count": self.chunk_count,
            "duration": duration,
            "average_chunk_size": (
                self.total_size / self.chunk_count if self.chunk_count > 0 else 0
            ),
            "chunks_per_second": self.chunk_count / duration if duration > 0 else 0,
            "bytes_per_second": self.total_size / duration if duration > 0 else 0,
        }


class StreamProcessor:
    """
    Processes streaming responses with event handling.

    This class handles the processing of streaming API responses,
    parsing SSE (Server-Sent Events) format and dispatching events.
    """

    def __init__(
        self,
        event_handler: Optional[Callable[[StreamEvent], None]] = None,
        buffer_size: int = 1024 * 1024,
    ):
        """
        Initialize stream processor.

        Args:
            event_handler: Optional event handler function
            buffer_size: Buffer size for streaming data
        """
        self.event_handler = event_handler
        self.buffer = StreamBuffer(buffer_size)
        self.events: List[StreamEvent] = []
        self.processing = False

    async def process_stream(
        self, response: aiohttp.ClientResponse
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Process a streaming response.

        Args:
            response: HTTP response with streaming data

        Yields:
            StreamEvent objects
        """
        self.processing = True

        try:
            # Send start event
            start_event = StreamEvent(
                event_type=StreamEventType.START,
                data=None,
                timestamp=time.time(),
                metadata={"status": response.status, "headers": dict(response.headers)},
            )
            yield start_event

            # Process chunks
            async for chunk in self._read_chunks(response):
                chunk_event = StreamEvent(
                    event_type=StreamEventType.CHUNK, data=chunk, timestamp=time.time()
                )

                self.events.append(chunk_event)
                if self.event_handler:
                    self.event_handler(chunk_event)

                yield chunk_event

            # Send end event
            end_event = StreamEvent(
                event_type=StreamEventType.END,
                data=self.buffer.get_content(),
                timestamp=time.time(),
                metadata=self.buffer.get_stats(),
            )
            yield end_event

        except Exception as e:
            error_event = StreamEvent(
                event_type=StreamEventType.ERROR,
                data=str(e),
                timestamp=time.time(),
                metadata={"error_type": type(e).__name__},
            )
            yield error_event

        finally:
            self.processing = False

    async def _read_chunks(
        self, response: aiohttp.ClientResponse
    ) -> AsyncGenerator[str, None]:
        """
        Read chunks from response.

        Args:
            response: HTTP response

        Yields:
            Data chunks
        """
        try:
            async for chunk in response.content.iter_chunked(8192):
                if chunk:
                    text = chunk.decode("utf-8", errors="replace")
                    self.buffer.add_chunk(text)
                    yield text

        except asyncio.CancelledError:
            logger.info("Stream processing cancelled")
            raise
        except Exception as e:
            logger.error(f"Error reading stream chunks: {e}")
            raise NetworkError(f"Stream reading failed: {e}")

    def get_events(self) -> List[StreamEvent]:
        """Get all processed events."""
        return self.events.copy()

    def get_content(self) -> str:
        """Get the complete streamed content."""
        return self.buffer.get_content()

    def get_stats(self) -> Dict[str, Any]:
        """Get streaming statistics."""
        return self.buffer.get_stats()


class SSEProcessor(StreamProcessor):
    """
    Server-Sent Events (SSE) processor for structured streaming.

    This class handles SSE format specifically, parsing event types
    and data according to the SSE specification.
    """

    def __init__(self, **kwargs):
        """Initialize SSE processor."""
        super().__init__(**kwargs)
        self.current_event = {}
        self.event_buffer = []

    async def _read_chunks(
        self, response: aiohttp.ClientResponse
    ) -> AsyncGenerator[str, None]:
        """
        Read and parse SSE chunks.

        Args:
            response: HTTP response

        Yields:
            Parsed event data
        """
        async for chunk in response.content.iter_chunked(8192):
            if chunk:
                text = chunk.decode("utf-8", errors="replace")
                self.buffer.add_chunk(text)

                # Parse SSE format
                lines = text.split("\n")
                for line in lines:
                    event_data = self._parse_sse_line(line)
                    if event_data:
                        yield event_data

    def _parse_sse_line(self, line: str) -> Optional[str]:
        """
        Parse a single SSE line.

        Args:
            line: SSE line to parse

        Returns:
            Event data if complete event is parsed
        """
        line = line.strip()

        if not line:
            # Empty line indicates end of event
            if self.current_event:
                event_data = self.current_event.get("data", "")
                self.current_event = {}
                return event_data
            return None

        if line.startswith(":"):
            # Comment line, ignore
            return None

        if ":" in line:
            field, value = line.split(":", 1)
            field = field.strip()
            value = value.strip()

            if field == "data":
                if "data" in self.current_event:
                    self.current_event["data"] += "\n" + value
                else:
                    self.current_event["data"] = value
            elif field == "event":
                self.current_event["event"] = value
            elif field == "id":
                self.current_event["id"] = value
            elif field == "retry":
                self.current_event["retry"] = int(value)

        return None


class StreamingResponseHandler:
    """
    High-level handler for streaming API responses.

    This class provides a simple interface for handling streaming
    responses with real-time display and processing.
    """

    def __init__(
        self,
        display_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """
        Initialize streaming response handler.

        Args:
            display_callback: Function to display streaming content
            progress_callback: Function to handle progress updates
        """
        self.display_callback = display_callback
        self.progress_callback = progress_callback
        self.processor = StreamProcessor()

    async def handle_stream(self, response: aiohttp.ClientResponse) -> str:
        """
        Handle a streaming response.

        Args:
            response: HTTP response with streaming data

        Returns:
            Complete response content
        """
        complete_content = ""

        async for event in self.processor.process_stream(response):
            if event.event_type == StreamEventType.START:
                logger.info("Stream started")
                if self.progress_callback:
                    self.progress_callback(
                        {"status": "started", "metadata": event.metadata}
                    )

            elif event.event_type == StreamEventType.CHUNK:
                complete_content += event.data
                if self.display_callback:
                    self.display_callback(event.data)

            elif event.event_type == StreamEventType.END:
                logger.info("Stream completed")
                if self.progress_callback:
                    self.progress_callback(
                        {"status": "completed", "stats": event.metadata}
                    )

            elif event.event_type == StreamEventType.ERROR:
                logger.error(f"Stream error: {event.data}")
                if self.progress_callback:
                    self.progress_callback({"status": "error", "error": event.data})
                raise APIError(f"Stream error: {event.data}")

        return complete_content

    def get_stats(self) -> Dict[str, Any]:
        """Get streaming statistics."""
        return self.processor.get_stats()


class AnthropicStreamHandler(StreamingResponseHandler):
    """
    Specialized handler for Anthropic API streaming responses.

    This class handles the specific format used by Anthropic's
    streaming API endpoints.
    """

    def __init__(self, **kwargs):
        """Initialize Anthropic stream handler."""
        super().__init__(**kwargs)
        self.processor = SSEProcessor()

    async def handle_stream(self, response: aiohttp.ClientResponse) -> str:
        """
        Handle Anthropic streaming response.

        Args:
            response: HTTP response with streaming data

        Returns:
            Complete response content
        """
        complete_content = ""

        async for event in self.processor.process_stream(response):
            if event.event_type == StreamEventType.START:
                logger.info("Anthropic stream started")
                if self.progress_callback:
                    self.progress_callback({"status": "started"})

            elif event.event_type == StreamEventType.CHUNK:
                # Parse Anthropic-specific event format
                try:
                    event_data = json.loads(event.data)
                    if event_data.get("type") == "content_block_delta":
                        delta = event_data.get("delta", {})
                        text = delta.get("text", "")
                        if text:
                            complete_content += text
                            if self.display_callback:
                                self.display_callback(text)

                except json.JSONDecodeError:
                    # Handle non-JSON chunks
                    if self.display_callback:
                        self.display_callback(event.data)

            elif event.event_type == StreamEventType.END:
                logger.info("Anthropic stream completed")
                if self.progress_callback:
                    self.progress_callback({"status": "completed"})

            elif event.event_type == StreamEventType.ERROR:
                logger.error(f"Anthropic stream error: {event.data}")
                raise APIError(f"Anthropic stream error: {event.data}")

        return complete_content


# Utility functions for easy streaming


async def stream_response(
    response: aiohttp.ClientResponse,
    display_callback: Optional[Callable[[str], None]] = None,
) -> str:
    """
    Simple utility to stream a response.

    Args:
        response: HTTP response
        display_callback: Optional callback to display chunks

    Returns:
        Complete response content
    """
    handler = StreamingResponseHandler(display_callback=display_callback)
    return await handler.handle_stream(response)


async def stream_anthropic_response(
    response: aiohttp.ClientResponse,
    display_callback: Optional[Callable[[str], None]] = None,
) -> str:
    """
    Utility to stream an Anthropic API response.

    Args:
        response: HTTP response from Anthropic API
        display_callback: Optional callback to display chunks

    Returns:
        Complete response content
    """
    handler = AnthropicStreamHandler(display_callback=display_callback)
    return await handler.handle_stream(response)
