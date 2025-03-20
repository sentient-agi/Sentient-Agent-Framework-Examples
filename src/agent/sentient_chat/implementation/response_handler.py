from __future__ import annotations
import json
from cuid2 import Cuid
from functools import wraps
from src.agent.sentient_chat.interface.exceptions import AgentError
from src.agent.sentient_chat.interface.events import (
    BaseEvent,
    DocumentEvent,
    DoneEvent,
    Event,
    ErrorContent,
    ErrorEvent,
    TextBlockEvent,
    DEFAULT_ERROR_CODE
)
from src.agent.sentient_chat.interface.identity import Identity
from src.agent.sentient_chat.implementation.id_handler import IdHandler
from src.agent.sentient_chat.implementation.text_stream_handler import TextStreamHandler
from typing import (
    Any,
    Callable,
    Mapping,
    Optional,
    Union,
    cast
)


class ResponseHandler:
    def __init__(
        self,
        source: Identity
    ):
        self._source = source
        self._id_handler = IdHandler()
        self._cuid_generator: Cuid = Cuid(length=10)
        self._streams: dict[str, TextStreamHandler] = {}
        self._is_complete = False


    @staticmethod
    def __verify_response_stream_is_open(func: Callable):
        @wraps(func)
        def wrapper(
                handler: ResponseHandler,
                *args, **kwargs
        ):
            if handler.is_complete:
                raise RuntimeError(
                    "Cannot send to a completed response handler."
                )
            return func(handler, *args, **kwargs)
        return wrapper
    

    @__verify_response_stream_is_open
    def respond(
        self,
        event_name: str,
        response: Union[Mapping[Any, Any] | str]
    ) -> BaseEvent:
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
        self.complete()
        return self.__finalise_event(event)

    
    @__verify_response_stream_is_open
    def create_json_event(
        self,
        event_name: str,
        data: Mapping[Any, Any]
    ) -> BaseEvent:
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
        return self.__finalise_event(event)

    
    @__verify_response_stream_is_open
    def create_text_event(
        self, 
        event_name: str, 
        content: str
    ) -> BaseEvent:
        """Send a single atomic text block response."""
        event = TextBlockEvent(
            source=self._source.id,
            event_name=event_name,
            content=content
        )
        return self.__finalise_event(event)


    @__verify_response_stream_is_open
    def create_text_stream_handler(
        self,
        event_name: str
    ) -> TextStreamHandler:
        """Create and return a new TextStream object."""
        stream_id = self._cuid_generator.generate()
        stream = TextStreamHandler(self._source, event_name, self._id_handler, stream_id)
        self._streams[stream_id] = stream
        return stream

    
    @__verify_response_stream_is_open
    def create_error_event(
        self,
        error_message: str,
        error_code: int = DEFAULT_ERROR_CODE,
        details: Optional[Mapping[str, Any]] = None
    ) -> BaseEvent:
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
        return self.__finalise_event(event)
    

    def create_done_event(self) -> BaseEvent:
        """Mark all streams as complete and the response as finished."""
        # Nop if already complete.
        if self.is_complete:
            return
        # Mark all streams as complete.
        for stream in self._streams.values():
            if not stream.is_complete:
                stream.complete()
        self._is_complete = True
        return self.__finalise_event(DoneEvent(source=self._source.id))


    def __finalise_event(self, event: Event) -> BaseEvent:
        event = cast(BaseEvent, event)
        event.id = self._id_handler.create_next_id(event.id)
        return event


    @property
    def is_complete(self) -> bool:
        """Return True if the response is complete."""
        return self._is_complete