from langgraph.graph import END, StateGraph

from app.graph.nodes.evaluator_node import evaluator_node
from app.graph.nodes.writer_node import writer_node
from app.graph.routing import route_after_evaluation
from app.graph.state import LinkedInAgentState


def build_workflow():
    graph = StateGraph(LinkedInAgentState)

    graph.add_node("writer", writer_node)
    graph.add_node("evaluator", evaluator_node)

    graph.set_entry_point("writer")

    graph.add_edge("writer", "evaluator")

    graph.add_conditional_edges(
        "evaluator",
        route_after_evaluation,
        {
            "writer": "writer",
            "human": END,
            "end": END,
        },
    )

    return graph.compile()