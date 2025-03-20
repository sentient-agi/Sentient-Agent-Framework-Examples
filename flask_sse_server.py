from flask import Flask, Response, request
from src.agent.agent import Agent
from src.agent.sentient_chat.interface.identity import Identity

app = Flask(__name__)
agent = Agent(Identity(id="SSE-Demo", name="SSE Demo"))       


def generate_data(query):
    for event in agent.search(query):
        yield f"data: {event}\n\n"


@app.route('/query')
def stream():
    query = request.get_json()["query"]
    return Response(generate_data(query), content_type='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True)