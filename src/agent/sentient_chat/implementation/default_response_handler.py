from __future__ import annotations
import inspect
import json
from cuid2 import Cuid
from functools import wraps
from src.agent.sentient_chat.interface.exceptions import (
    AgentError,
    ResponseStreamClosedError
)
from src.agent.sentient_chat.interface.events import (
    DocumentEvent,
    DoneEvent,
    ErrorContent,
    ErrorEvent,
    StreamEvent,
    TextBlockEvent,
    DEFAULT_ERROR_CODE
)
from src.agent.sentient_chat.interface.hook import Hook
from src.agent.sentient_chat.interface.identity import Identity
from src.agent.sentient_chat.interface.stream_event_emitter import StreamEventEmitter
from src.agent.sentient_chat.implementation.default_text_stream import DefaultTextStream
from typing import (
    Any,
    Callable,
    Mapping,
    Optional,
    Union
)


class DefaultResponseHandler:
    def __init__(
        self,
        source: Identity,
        hook: Hook
    ):
        self._source = source
        self._hook = hook
        self._cuid_generator: Cuid = Cuid(length=10)
        self._streams: dict[str, StreamEventEmitter] = {}
        self._is_complete = False


    @staticmethod
    def __verify_response_stream_is_open(func: Callable):
        """Check if the response stream is open."""
        is_async_def = inspect.iscoroutinefunction(func)

        @wraps(func)
        async def async_wrapper(
                handler: DefaultResponseHandler,
                *args, **kwargs
        ):
            if handler.is_complete:
                raise ResponseStreamClosedError(
                    "Cannot send to a completed response handler."
                )
            return await func(handler, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(
                handler: DefaultResponseHandler,
                *args, **kwargs
        ):
            if handler.is_complete:
                raise RuntimeError(
                    "Cannot send to a completed response handler."
                )
            return func(handler, *args, **kwargs)
        return async_wrapper if is_async_def else sync_wrapper
    

    @__verify_response_stream_is_open
    async def respond(
        self,
        event_name: str,
        response: Union[Mapping[Any, Any] | str]
    ) -> None:
        """Syncronus function to Send a single atomic event as complete response for request. """
        event: TextBlockEvent | DocumentEvent | None = None
        match response:
            case str():
                event = TextBlockEvent(
                    source=self._source.id,
                    event_name=event_name,
                    content=response
                )
            case _:
                try:
                    json.dumps(response)
                except TypeError as e:
                    raise AgentError(
                        "Response content must be JSON serializable"
                    ) from e
                event = DocumentEvent(
                    source=self._source.id,
                    event_name=event_name,
                    content=response
                )
        await self.__emit_event(event)
        await self.complete()

    
    @__verify_response_stream_is_open
    async def __send_event_chunk(
        self, 
        chunk: StreamEvent
    ) -> None:
        """Send a chunk of text to a stream."""
        await self.__emit_event(chunk)

    
    @__verify_response_stream_is_open
    async def emit_json(
        self,
        event_name: str,
        data: Mapping[Any, Any]
    ) -> None:
        """Send a single atomic JSON response."""
        try:
            json.dumps(data)
        except TypeError as e:
            raise AgentError(
                "Response content must be JSON serializable"
            ) from e
        event = DocumentEvent(
            source=self._source.id,
            event_name=event_name,
            content=data
        )
        await self.__emit_event(event)

    
    @__verify_response_stream_is_open
    async def emit_text_block(
        self, 
        event_name: str, 
        content: str
    ) -> None:
        """Send a single atomic text block response."""
        event = TextBlockEvent(
            source=self._source.id,
            event_name=event_name,
            content=content
        )
        await self.__emit_event(event)


    @__verify_response_stream_is_open
    def create_text_stream(
        self,
        event_name: str
    ) -> DefaultTextStream:
        """Create and return a new TextStream object."""
        stream_id = self._cuid_generator.generate()
        stream = DefaultTextStream(self._source, event_name, stream_id, self._hook)
        self._streams[stream_id] = stream
        return stream

    
    @__verify_response_stream_is_open
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
            source=self._source.id,
            event_name="error",
            content=error_content
        )
        await self.__emit_event(event)


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
        await self.__emit_event(
            DoneEvent(source=self._source.id))


    async def __emit_event(self, event) -> None:
        """Internal method to emit events."""
        await self._hook.emit(event)