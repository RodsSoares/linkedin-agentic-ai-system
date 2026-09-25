from app.components.perspective_generation import generate_perspective_set
from app.graph.state import LinkedInAgentState


def perspective_generation_node(
    state: LinkedInAgentState,
) -> dict:
    argument_brief = state.get("argument_brief")

    if argument_brief is None:
        raise ValueError(
            "Perspective Generation node requires an ArgumentBrief."
        )

    perspective_set = generate_perspective_set(argument_brief)

    return {
        "perspective_set": perspective_set,
    }
