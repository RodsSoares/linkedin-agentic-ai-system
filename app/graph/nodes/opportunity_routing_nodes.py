from app.graph.state import LinkedInAgentState


def accepted_for_research_node(
    state: LinkedInAgentState,
) -> dict:
    return {
        "next_step": "research",
        "status": "ACCEPTED_FOR_RESEARCH",
    }


def queued_opportunity_node(
    state: LinkedInAgentState,
) -> dict:
    return {
        "next_step": "queue",
        "status": "QUEUED",
    }