# Search-Agent-SSE-Example

## Key Points of This Implementation:

### StreamEventEmitter:
This class manages event streaming. It uses an asyncio.Queue to hold the events and then sends them through the HTTP response stream.

### ResponseHandler:
This class contains methods for handling different types of responses like emit_json, emit_text_block, and error responses. It also contains complete and is_complete for tracking whether the response is finished.

### SSERequestHandler:
This is a custom request handler that uses the built-in BaseHTTPRequestHandler to handle SSE requests. It listens on /sse, sets the correct headers for SSE, and uses the StreamEventEmitter to send messages.

### asyncio.run():
Since http.server is synchronous, we need to use asyncio.run() to run asynchronous operations like sending and streaming events.

## No External Dependencies:
This implementation relies on Python's built-in http.server and asyncio for asynchronous functionality, keeping dependencies minimal.

## Running the Server:
1. **Run the Script:** Simply run the Python script, and the server will start listening on http://localhost:8080.
2. **Access the SSE Stream:** You can test the SSE endpoint by navigating to http://localhost:8080/sse in your browser or by using curl:
curl http://localhost:8080/sse
3. **Server Behavior:** The server will keep the connection open and send three event messages (First message, Second message, and Third message).
Once the messages are sent, the server will complete the stream.

## Notes:
- This server uses minimal external dependencies (just Python's built-in libraries) while still supporting the core functionality of SSE and responding asynchronously.
- The server is designed to be simple and extendable. You can easily modify it to handle more complex event streaming, including error handling and various content types.