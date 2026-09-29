from langgraph.types import interrupt

from app.graph.state import LinkedInAgentState


VALID_FINAL_REFINEMENT_ACTIONS = {
    "accept",
    "refine",
}


def human_final_refinement_node(
    state: LinkedInAgentState,
) -> dict:
    current_draft = state.get("current_draft")
    quality_evaluation = state.get("quality_evaluation")

    if not current_draft:
        raise ValueError(
            "Human Final Refinement node requires a current draft."
        )

    if quality_evaluation is None:
        raise ValueError(
            "Human Final Refinement node requires a quality evaluation."
        )

    if quality_evaluation.decision != "PASS":
        raise ValueError(
            "Human Final Refinement node requires a PASS quality evaluation."
        )

    human_decision = interrupt(
        {
            "type": "final_refinement",
            "current_draft": current_draft,
            "allowed_actions": [
                "accept",
                "refine",
            ],
            "refinement_dimensions": [
                "tone",
                "emphasis",
                "length",
                "framing",
                "closing",
            ],
        }
    )

    if not isinstance(human_decision, dict):
        raise ValueError(
            "Human final refinement decision must be a dictionary."
        )

    action = human_decision.get("action")

    if action not in VALID_FINAL_REFINEMENT_ACTIONS:
        raise ValueError(
            "Human final refinement decision requires a valid action."
        )

    guidance = human_decision.get("guidance")

    if action == "refine":
        if not isinstance(guidance, str) or not guidance.strip():
            raise ValueError(
                "Final refinement guidance must be a non-empty string "
                "when action is refine."
            )

        guidance = guidance.strip()

    else:
        guidance = None

    return {
        "final_refinement_action": action,
        "final_refinement_guidance": guidance,
    }
