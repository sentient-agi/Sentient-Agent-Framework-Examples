from cuid2 import Cuid
from .events import TextChunkEvent
from .identity import Identity


cuid_generator: Cuid = Cuid(length=10)


class TextStream():
    def __init__(
        self,
        event_source: Identity,
        event_name: str
    ):
        cuid_generator: Cuid = Cuid(length=10)
        self._event_source = event_source
        self._event_name = event_name
        self._stream_id = cuid_generator.generate()
        self._is_complete = False


    def create_chunk(
        self, 
        chunk: str
    ) -> TextChunkEvent:
        if self._is_complete:
            raise Exception(
                f"Cannot emit chunk to closed stream {self._stream_id}."
            )
        event = TextChunkEvent(
            source=self._event_source.id,
            event_name=self._event_name,
            stream_id=self._stream_id,
            is_complete=False,
            content=chunk
        )
        return event


    def complete(self) -> None:
        """Mark this stream as complete."""
        event = TextChunkEvent(
            source=self._event_source.id,
            event_name=self._event_name,
            stream_id=self._stream_id,
            is_complete=True,
            content=" "
        )
        return event


    @property
    def id(self) -> str:
        """Get the stream ID."""
        return self._stream_id


    @property
    def is_complete(self) -> bool:
        """Check if the stream is complete."""
        return self._is_complete