from __future__ import annotations
from src.agent.sentient_chat.interface.exceptions import TextStreamClosedError
from src.agent.sentient_chat.interface.events import (
    BaseEvent,
    Event,
    TextChunkEvent
)
from src.agent.sentient_chat.interface.identity import Identity
from src.agent.sentient_chat.implementation.id_handler import IdHandler
from typing import cast


class TextStreamHandler():
    def __init__(
        self,
        event_source: Identity,
        event_name: str,
        event_id_handler: IdHandler,
        stream_id: str,
    ):
        self._event_source = event_source
        self._event_name = event_name
        self._event_id_handler = event_id_handler
        self._stream_id = stream_id
        self._is_complete = False


    def create_stream_chunk_event(
        self, 
        chunk: str
    ) -> TextChunkEvent:
        """Send a chunk of text to this stream."""
        if self._is_complete:
            raise TextStreamClosedError(
                f"Cannot emit chunk to closed stream {self._stream_id}."
            )
        event = TextChunkEvent(
            source=self._event_source.id,
            event_name=self._event_name,
            stream_id=self._stream_id,
            is_complete=False,
            content=chunk
        )
        return self.__finalise_event(event)


    def create_stream_complete_event(self) -> TextChunkEvent:
        """Mark this stream as complete."""
        event = TextChunkEvent(
            source=self._event_source.id,
            event_name=self._event_name,
            stream_id=self._stream_id,
            is_complete=True,
            content=" "
        )
        self._is_complete = True
        return self.__finalise_event(event)


    def __finalise_event(self, event: Event) -> BaseEvent:
        event = cast(BaseEvent, event)
        event.id = self._event_id_handler.create_next_id(event.id)
        return event


    @property
    def id(self) -> str:
        """Get the stream ID."""
        return self._stream_id


    @property
    def is_complete(self) -> bool:
        """Check if the stream is complete."""
        return self._is_complete