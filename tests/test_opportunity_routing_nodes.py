from app.graph.nodes.opportunity_routing_nodes import (
    accepted_for_research_node,
    queued_opportunity_node,
)


def test_accepted_for_research_node_sets_expected_state():
    state = {}

    result = accepted_for_research_node(state)

    assert result == {
        "next_step": "research",
        "status": "ACCEPTED_FOR_RESEARCH",
    }


def test_queued_opportunity_node_sets_expected_state():
    state = {}

    result = queued_opportunity_node(state)

    assert result == {
        "next_step": "queue",
        "status": "QUEUED",
    }