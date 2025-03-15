import asyncio
import threading
from flask import Flask, Response, request
from queue import Queue, ShutDown
from src.agent.agent import Agent


app = Flask(__name__)
agent = Agent(response_queue=Queue())


def generate_data(query):
    threading.Thread(target=lambda: asyncio.run(agent.search(query))).start()
    while True:
        try:
            event = agent.response_queue.get()
            yield f"data: {event}\n\n"
        except ShutDown:
            print("Queue shutdown")
            return


@app.route('/query')
def stream():
    query = request.get_json()["query"]
    return Response(generate_data(query), content_type='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True)