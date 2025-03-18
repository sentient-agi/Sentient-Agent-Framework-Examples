# Search Agent SSE Example

This is a simple example demonstrating how to set up agent that is compatible with SentientChat. It uses a Flask server that connects to an agent and streams responses to a client using Server-Sent Events (SSE).

> [!NOTE]
> **These instructions are for unix-based systems (i.e. MacOS, Linux). Before you proceed, make sure that you have installed `python` and `pip`. If you have not, follow [these](https://packaging.python.org/en/latest/tutorials/installing-packages/) instructions to do so.**

> [!WARNING]
> **The format of the messages returned by the server is important. Read more [here](https://html.spec.whatwg.org/multipage/server-sent-events.html).**

#### 1. Create Python virtual environment:
```
python3 -m venv .venv
```

#### 2. Activate Python virtual environment:
```
source .venv/bin/activate
```

#### 3. Install dependencies:
```
pip install -r requirements.txt
```

#### 4. Run the script:
```
python3 flask_sse_server.py
```

#### 5. Use a tool like [CuRL](https://curl.se/) or [Postman](https://www.postman.com/) to query the server:
```
curl --location --request GET 'http://127.0.0.1:5000/query' \
--header 'Content-Type: application/json' \
--data '{
    "query": "Who is Lionel Messi?"
}'
```
Expected output:
```

data: content_type=<EventContentType...

... 
```


## SentientChat Interfaces
### Events
SentientChat uses a custom event system for agent responses. The system is designed to be compatible with Server-Sent Events (SSE), so that updates can be pushed in real-time. This is particularly useful for streaming responses from an AI agent, where you might want to show the response as it's being generated rather than waiting for the complete response.

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

### Identity
SentientChat uses an `Identity` object to identify the source of an event (typically an agent). It contains an `id` and a `name`.