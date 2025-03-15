from typing import (
    Any,
    Generic,
    Mapping,
    Optional,
    Protocol,
    TypeVar,
    Union,
)
from src.agent.sentient_chat.interface.events import DEFAULT_ERROR_CODE


T_contra = TypeVar('T_contra', contravariant=True)


class StreamEventEmitter(Protocol, Generic[T_contra]):
    async def complete(self) -> None:
        """Mark this stream as complete."""


    def id(self) -> str:
        """Get the stream ID."""


    def is_complete(self) -> bool:
        """Check if the stream is complete."""


    async def emit_chunk(self, chunk: T_contra):
        """ Send event chunk to this stream"""


class ResponseHandler(Protocol):
    def respond(
            self,
            event_name: str,
            response: Union[Mapping[Any, Any], str]
    ) -> None:
        """Send a single atomic event as a complete response."""


    async def emit_json(
            self,
            event_name: str,
            data: Mapping[Any, Any]
    ) -> None:
        """Send a single atomic JSON response."""


    async def emit_text_block(
            self,
            event_name: str,
            content: str
    ) -> None:
        """Send a single atomic text block response."""


    def create_text_stream(self, event_name: str) -> StreamEventEmitter[str]:
        """Create and return a new TextStream object."""


    async def emit_error(
            self,
            error_message: str,
            error_code: int = DEFAULT_ERROR_CODE,
            details: Optional[Mapping[str, Any]] = None
    ) -> None:
        """Send an error event."""


    async def complete(self) -> None:
        """Mark all streams as complete and the response as finished."""


    def is_complete(self) -> bool:
        """Return true if the response is marked complete, false otherwise."""