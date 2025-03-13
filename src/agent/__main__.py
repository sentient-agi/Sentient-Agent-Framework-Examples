from .agent import Agent

try:
    print("Agent starting up...")
    agent = Agent()
    agent.run()
except KeyboardInterrupt:
    print("Agent shutting down...")
    exit()