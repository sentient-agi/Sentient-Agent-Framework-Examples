import asyncio
import threading
from flask import Flask, Response, request
from queue import Queue
from src.agent.agent import Agent
from src.agent.sentient_agent.interface.identity import Identity
from src.agent.sentient_agent.interface.events import DoneEvent


app = Flask(__name__)
response_queue=Queue()
agent = Agent(
    identity=Identity(id="SSE-Demo", name="SSE Demo"),
    response_queue=response_queue
)


def generate_data(query):
    threading.Thread(target=lambda: asyncio.run(agent.search(query))).start()
    while True:
        event = response_queue.get()
        yield f"data: {event}\n\n"
        if type(event) == DoneEvent:
            break
        


@app.route('/query')
def stream():
    query = request.get_json()["query"]
    return Response(generate_data(query), content_type='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True)