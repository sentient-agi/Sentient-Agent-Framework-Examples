from ..interface.response_handler import StreamEventEmitter
from src.agent.sentient_chat.interface.events import (
    DocumentEvent,
    DoneEvent,
    ErrorContent,
    ErrorEvent,
    StreamEvent,
    TextBlockEvent,
    DEFAULT_ERROR_CODE
)
from queue import Queue
from .SSE_text_stream import TextStream
from typing import (
    Any,
    Mapping,
    Optional,
    Union
)

import json
import uuid

class SSEResponseHandler:
    def __init__(
            self,
            response_queue: Queue
    ):
        self.id = str(uuid.uuid4())
        self._is_complete = False
        self._response_queue = response_queue
        self._streams: dict[str, StreamEventEmitter] = {}

    
    async def respond(
            self,
            event_name: str,
            response: Union[Mapping[Any, Any] | str]
    ) -> None:
        """ syncronus function to Send a single atomic event as complete response for request. """
        event: TextBlockEvent | DocumentEvent | None = None
        match response:
            case str():
                event = TextBlockEvent(
                    source=self.id,
                    event_name=event_name,
                    content=response
                )
            case _:
                try:
                    json.dumps(response)
                except TypeError as e:
                    raise Exception(
                        "Response content must be JSON serializable"
                    ) from e
                event = DocumentEvent(
                    source=self.id,
                    event_name=event_name,
                    content=response
                )
        await self._emit_event(event)
        await self.complete()

    
    async def _send_event_chunk(self, chunk: StreamEvent) -> None:
        """Send a chunk of text to a stream."""
        await self._emit_event(chunk)

    
    async def emit_json(
        self, event_name: str, data: Mapping[Any, Any]
    ) -> None:
        """Send a single atomic JSON response."""
        try:
            json.dumps(data)
        except TypeError as e:
            raise Exception(
                "Response content must be JSON serializable"
            ) from e
        event = DocumentEvent(
            source=self.id,
            event_name=event_name,
            content=data
        )

        await self._emit_event(event)

    
    async def emit_text_block(self, event_name: str, content: str) -> None:
        """Send a single atomic text block response."""
        event = TextBlockEvent(
            source=self.id,
            event_name=event_name,
            content=content
        )
        await self._emit_event(event)

    
    def create_text_stream(self, event_name: str) -> TextStream:
        """Create and return a new TextStream object."""
        stream_id = str(uuid.uuid4())
        stream = TextStream(self.id, event_name, stream_id, self._response_queue)
        self._streams[stream_id] = stream
        return stream

    
    async def emit_error(
            self,
            error_message: str,
            error_code: int = DEFAULT_ERROR_CODE,
            details: Optional[Mapping[str, Any]] = None
    ) -> None:
        """Send an error event."""
        error_content = ErrorContent(
            error_message=error_message,
            error_code=error_code,
            details=details
        )
        event = ErrorEvent(
            source=self.id,
            event_name="error",
            content=error_content
        )
        await self._emit_event(event)


    @property
    def is_complete(self) -> bool:
        """Return True if the response is complete."""
        return self._is_complete


    async def complete(self) -> None:
        """Mark all streams as complete and the response as finished."""
        # Nop if already complete.
        if self.is_complete:
            return
        # Mark all streams as complete.
        for stream in self._streams.values():
            if not stream.is_complete:
                await stream.complete()
        self._is_complete = True
        await self._emit_event(
            DoneEvent(source=self.id))
        self._response_queue.shutdown()


    async def _emit_event(self, event) -> None:
        """
        Internal method to emit events. Override this in subclasses to handle
        event delivery.
        """
        self._response_queue.put(event)