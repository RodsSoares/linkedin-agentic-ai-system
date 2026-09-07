from app.graph.state import LinkedInAgentState


MAX_ITERATIONS = 3


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