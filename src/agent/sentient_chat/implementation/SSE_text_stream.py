from ..interface.response_handler import StreamEventEmitter
from ..interface.events import TextChunkEvent
from queue import Queue

class TextStream(StreamEventEmitter[str]):
    def __init__(
            self,
            event_source: str,
            event_name: str,
            stream_id: str,
            response_queue: Queue
    ):
        self._event_source = event_source
        self._event_name = event_name
        self._stream_id = stream_id
        self._response_queue = response_queue
        self._is_complete = False


    async def emit_chunk(self, chunk: str) -> None:
        """Send a chunk of text to this stream."""
        if self._is_complete:
            raise Exception(
                f"Cannot emit chunk to closed stream {self._stream_id}."
            )
        event = TextChunkEvent(
            source=self._event_source,
            event_name=self._event_name,
            stream_id=self._stream_id,
            is_complete=False,
            content=chunk
        )
        self._response_queue.put(event)


    async def complete(self) -> None:
        """Mark this stream as complete."""
        event = TextChunkEvent(
            source=self._event_source,
            event_name=self._event_name,
            stream_id=self._stream_id,
            is_complete=True,
            content=" "
        )
        self._response_queue.put(event)
        self._is_complete = True
        print("Stream complete")


    @property
    def id(self) -> str:
        """Get the stream ID."""
        return self._stream_id


    @property
    def is_complete(self) -> bool:
        """Check if the stream is complete."""
        return self._is_complete