from langgraph.graph import END, StateGraph

from app.graph.nodes.evaluator_node import evaluator_node
from app.graph.nodes.opportunity_evaluator_node import (
    opportunity_evaluator_node,
)
from app.graph.nodes.opportunity_routing_nodes import (
    accepted_for_research_node,
    queued_opportunity_node,
)
from app.graph.nodes.research_node import research_node
from app.graph.nodes.scout_node import scout_node
from app.graph.nodes.writer_node import writer_node
from app.graph.routing import (
    route_after_evaluation,
    route_after_opportunity_evaluation,
    route_after_scout,
)
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


def build_opportunity_workflow():
    graph = StateGraph(LinkedInAgentState)

    graph.add_node(
        "opportunity_evaluator",
        opportunity_evaluator_node,
    )
    graph.add_node(
        "accepted_for_research",
        accepted_for_research_node,
    )
    graph.add_node(
        "research",
        research_node,
    )
    graph.add_node(
        "writer",
        writer_node,
    )
    graph.add_node(
        "queued",
        queued_opportunity_node,
    )

    graph.set_entry_point("opportunity_evaluator")
    graph.add_conditional_edges(
        "opportunity_evaluator",
        route_after_opportunity_evaluation,
        {
            "continue": "accepted_for_research",
            "queue": "queued",
            "end": END,
        },
    )

    graph.add_edge(
        "accepted_for_research",
        "research",
    )
    graph.add_edge(
        "research",
        "writer",
    )
    graph.add_edge(
        "writer",
        END,
    )
    graph.add_edge(
        "queued",
        END,
    )

    return graph.compile()


def build_scout_opportunity_workflow():
    graph = StateGraph(LinkedInAgentState)

    graph.add_node(
        "scout",
        scout_node,
    )
    graph.add_node(
        "opportunity_evaluator",
        opportunity_evaluator_node,
    )
    graph.add_node(
        "accepted_for_research",
        accepted_for_research_node,
    )
    graph.add_node(
        "research",
        research_node,
    )
    graph.add_node(
        "writer",
        writer_node,
    )
    graph.add_node(
        "queued",
        queued_opportunity_node,
    )

    graph.set_entry_point("scout")
    graph.add_conditional_edges(
        "scout",
        route_after_scout,
        {
            "opportunity_evaluation": "opportunity_evaluator",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "opportunity_evaluator",
        route_after_opportunity_evaluation,
        {
            "continue": "accepted_for_research",
            "queue": "queued",
            "end": END,
        },
    )

    graph.add_edge(
        "accepted_for_research",
        "research",
    )
    graph.add_edge(
        "research",
        "writer",
    )
    graph.add_edge(
        "writer",
        END,
    )
    graph.add_edge(
        "queued",
        END,
    )

    return graph.compile()
