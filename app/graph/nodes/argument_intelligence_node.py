from app.components.argument_intelligence import generate_argument_brief
from app.graph.state import LinkedInAgentState


def argument_intelligence_node(
    state: LinkedInAgentState,
) -> dict:
    research_brief = state.get("research_result")

    if research_brief is None:
        raise ValueError(
            "Argument Intelligence node requires a ResearchBrief."
        )

    argument_brief = generate_argument_brief(research_brief)

    return {
        "argument_brief": argument_brief,
    }