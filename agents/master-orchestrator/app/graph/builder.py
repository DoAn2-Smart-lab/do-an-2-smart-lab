"""
Dung LangGraph StateGraph dung 5 node mo ta trong README.md.
"""
from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    classify_intent,
    receive_input,
    reply_user,
    route_to_agent,
    wait_response,
)
from app.graph.state import OrchestratorState


def build_graph():
    graph = StateGraph(OrchestratorState)

    graph.add_node("receive_input", receive_input)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("route_to_agent", route_to_agent)
    graph.add_node("wait_response", wait_response)
    graph.add_node("reply_user", reply_user)

    graph.add_edge(START, "receive_input")
    graph.add_edge("receive_input", "classify_intent")
    graph.add_edge("classify_intent", "route_to_agent")
    graph.add_edge("route_to_agent", "wait_response")
    graph.add_edge("wait_response", "reply_user")
    graph.add_edge("reply_user", END)

    return graph.compile()
