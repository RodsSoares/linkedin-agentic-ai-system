from app.graph.state import LinkedInAgentState


MAX_ITERATIONS = 3

def route_after_scout(
    state: LinkedInAgentState,
) -> str:
    post = state.get("post")

    if post is not None:
        return "opportunity_evaluation"

    if state.get("status") == "NO_CANDIDATE_FOUND":
        return "end"

    raise ValueError(
        "Scout routing requires either a selected post "
        "or NO_CANDIDATE_FOUND status."
    )


def route_after_opportunity_evaluation(
    state: LinkedInAgentState,
) -> str:
    evaluation = state["opportunity_evaluation"]

    if evaluation is None:
        raise ValueError(
            "Routing requires an opportunity evaluation."
        )

    classification = evaluation.classification

    if classification == "HIGH":
        return "continue"

    if classification == "MEDIUM":
        return "queue"

    if classification == "LOW":
        return "end"

    raise ValueError(
        f"Unknown opportunity classification: {classification}"
    )


def route_after_evaluation(state: LinkedInAgentState) -> str:
    evaluation = state["quality_evaluation"]

    if evaluation is None:
        raise ValueError("Routing requires a quality evaluation.")

    decision = evaluation.decision

    if decision == "PASS":
        return "human"

    if decision == "REVISE":
        if state["iteration"] >= MAX_ITERATIONS:
            return "end"

        return "writer"

    if decision == "REJECT":
        return "end"

    raise ValueError(f"Unknown evaluation decision: {decision}")


def route_after_final_refinement(
    state: LinkedInAgentState,
) -> str:
    action = state.get("final_refinement_action")

    if action == "accept":
        return "end"

    if action == "refine":
        return "writer"

    raise ValueError(
        "Final refinement routing requires a valid action."
    )


def route_after_writer(
    state: LinkedInAgentState,
) -> str:
    next_step = state.get("next_step")

    if next_step == "evaluator":
        return "evaluator"

    if next_step == "final":
        return "end"

    raise ValueError(
        "Writer routing requires a valid next_step."
    )
