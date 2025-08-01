from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.pregel import RetryPolicy

from src.ai_agents.text_agents import (
    State,
    information_assistant_agent
)

retry_policy = RetryPolicy(
    initial_interval=0.3,
    backoff_factor=1.2,
    max_attempts=3,
    retry_on=lambda e: True # retry on all exceptions. Comment this to debug
) 

graph = StateGraph(State)
graph.add_node("information_assistant_agent", information_assistant_agent, retry=retry_policy)
graph.add_edge(START, "information_assistant_agent")
graph.add_edge("information_assistant_agent", END)

checkpointer = InMemorySaver()
assistant_bot = graph.compile(checkpointer=checkpointer)