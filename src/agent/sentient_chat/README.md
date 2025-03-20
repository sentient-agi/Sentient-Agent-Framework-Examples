# SentientChat

## ResponseHandler
The `ResponseHandler` is responsible for creating events to send to the SentientChat client. It abstracts away the event system and provides a simple interface for sending events to the client. It is initialized with your agent's SentientChat `Identity` and with a `Hook` that is to direct the events to the client:

```python
from sentientchat import DefaultHook, DefaultResponseHandler, Identity

identity = Identity(id="my-agent-id", name="My Agent")
hook = DefaultHook(self._response_queue)
response_handler = DefaultResponseHandler(identity, hook)
```

Once initialized, you can use the `ResponseHandler` to create events that will be emitted using the `Hook`. You should use a new `ResponseHandler` for each agent query.

Text events are used to send a single, complete message to the client.
```python
yield response_handler.emit_text_block(
    "SEARCH", "Searching internet for results..."
)
```

JSON events are used to send a JSON object to the client.
```
yield response_handler.emit_json(
    "SOURCES", {"results": search_results["results"]}
)
```

Error events are used to send an error message to the client.
```
yield response_handler.emit_error(
    "ERROR", {"message": "An error occurred"}
)
```

At the end of a response, you should call `complete` to signal the end of the response. This will emit a `DoneEvent` using the `Hook`.
```
response_handler.complete()
```

To stream a longer response piece by piece, you can use the `create_text_stream_handler` method. This returns a `TextStreamHandler` object that you can use to stream text to the client using the `create_stream_chunk_event` method. You must call `create_stream_complete_event` when you are done streaming.
```
final_response_stream = response_handler.create_text_stream(
    "FINAL_RESPONSE"
    )
for chunk in self.__process_search_results(search_results["results"]):
    await final_response_stream.emit_chunk(chunk)
await final_response_stream.complete()
```

The code snippets above are from an example search agent that can be found [here](https://github.com/sentient-xyz/Search-Agent-SSE-Example).


## Technical Details
#### Identity
SentientChat uses an `Identity` object to identify the source of an event (typically an agent). It contains an `id` and a `name`.

#### Events
SentientChat uses a custom event system for agent responses. This is particularly useful for streaming responses from an AI agent, when you might want to show the agent's work while the response is being generated, rather than having the user wait for the final response.

1. **Atomic Events** (single, complete messages):
   - `DocumentEvent`: For sending JSON data
   - `TextBlockEvent`: For sending a complete block of text
   - `ErrorEvent`: For sending error messages
   - `DoneEvent`: To signal completion

2. **Chunked/Stream Events**:
   - `TextChunkEvent`: For streaming text responses piece by piece

Each event has:
- A `content_type` to identify what kind of event it is
- An `event_name` to identify the specific event
- A `source` to identify where it came from
- Optional `metadata` for additional information
- Unique `id` using ULID (Universal Lexicographically sortable Unique IDentifier)

The events follow a clear hierarchy:
```
Event (base class)
└── BaseEvent
    ├── AtomicEvent (single messages)
    │   ├── DocumentEvent (JSON)
    │   ├── TextBlockEvent (text)
    │   ├── ErrorEvent
    │   └── DoneEvent
    └── StreamEvent
        └── TextChunkEvent (streaming text)
```