from langgraph.types import interrupt

from app.graph.state import LinkedInAgentState
from app.schemas.writer import ContentMode


VALID_CONTENT_MODES: set[ContentMode] = {
    "linkedin_post",
    "linkedin_reply",
    "article",
}


def human_content_mode_selection_node(
    state: LinkedInAgentState,
) -> dict:
    selected_perspective = state.get("selected_perspective")

    if selected_perspective is None:
        raise ValueError(
            "Human Content Mode Selection node requires a SelectedPerspective."
        )

    human_decision = interrupt(
        {
            "type": "content_mode_selection",
            "content_modes": [
                {
                    "id": "linkedin_post",
                    "label": "LinkedIn Post",
                },
                {
                    "id": "linkedin_reply",
                    "label": "LinkedIn Reply",
                },
                {
                    "id": "article",
                    "label": "Article",
                },
            ],
        }
    )

    if not isinstance(human_decision, dict):
        raise ValueError(
            "Human content mode decision must be a dictionary."
        )

    content_mode = human_decision.get("content_mode")

    if content_mode not in VALID_CONTENT_MODES:
        raise ValueError(
            "Human content mode decision requires a valid content_mode."
        )

    return {
        "content_mode": content_mode,
    }
