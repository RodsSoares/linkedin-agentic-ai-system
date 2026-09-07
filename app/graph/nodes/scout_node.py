from app.agents.scout import run_scout
from app.graph.state import LinkedInAgentState


def scout_node(state: LinkedInAgentState) -> dict:
    objective = state.get("scout_objective")

    if not objective:
        raise ValueError(
            "Scout workflow requires a scout_objective."
        )

    scout_state = run_scout(objective=objective)

    if not scout_state.candidates:
        return {
            "post": None,
            "status": "NO_CANDIDATE_FOUND",
            "next_step": "end",
        }

    if len(scout_state.candidates) > 1:
        raise ValueError(
            "Scout produced multiple candidates, but multi-candidate "
            "workflow handling is not implemented yet."
        )

    return {
        "post": scout_state.candidates[0],
        "status": "CANDIDATE_SELECTED",
        "next_step": "opportunity_evaluation",
    }