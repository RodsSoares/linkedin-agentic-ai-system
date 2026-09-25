from langgraph.types import interrupt

from app.components.perspective_selection import select_perspective
from app.graph.state import LinkedInAgentState


def human_perspective_selection_node(
    state: LinkedInAgentState,
) -> dict:
    perspective_set = state.get("perspective_set")

    if perspective_set is None:
        raise ValueError(
            "Human Perspective Selection node requires a PerspectiveSet."
        )

    human_decision = interrupt(
        {
            "type": "perspective_selection",
            "perspectives": [
                perspective.model_dump(mode="json")
                for perspective in perspective_set.perspectives
            ],
        }
    )

    if not isinstance(human_decision, dict):
        raise ValueError(
            "Human perspective decision must be a dictionary."
        )

    perspective_id = human_decision.get("perspective_id")

    if not isinstance(perspective_id, str):
        raise ValueError(
            "Human perspective decision requires a perspective_id."
        )

    human_guidance = human_decision.get("human_guidance")

    if human_guidance is not None and not isinstance(human_guidance, str):
        raise ValueError(
            "human_guidance must be a string or None."
        )

    selected_perspective = select_perspective(
        perspective_set=perspective_set,
        perspective_id=perspective_id,
        human_guidance=human_guidance,
    )

    return {
        "selected_perspective": selected_perspective,
    }
