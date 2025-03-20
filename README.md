# Search Agent SSE Example

This is a simple example demonstrating how to set up an agent that is compatible with SentientChat. It uses a Flask server that can be used to query a search agent and that streams the agent's responses to a client using Server-Sent Events (SSE).

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

#### 4. Run the server:
```
python3 flask_sse_server.py
```

#### 5. Use a tool like [CuRL](https://curl.se/) or [Postman](https://www.postman.com/) to query the server. It exposes a single `:query` endpoint that can be used to query the agent:
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