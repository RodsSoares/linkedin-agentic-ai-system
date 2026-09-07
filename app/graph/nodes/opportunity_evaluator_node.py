from app.components.opportunity_evaluator import evaluate_opportunity_semantics
from app.components.opportunity_scoring import evaluate_opportunity
from app.graph.state import LinkedInAgentState


DEFAULT_ENGAGEMENT_POTENTIAL = 50


def opportunity_evaluator_node(
    state: LinkedInAgentState,
) -> dict:
    post = state["post"]

    if post is None:
        raise ValueError(
            "Opportunity evaluation requires a PostCandidate."
        )

    signals = evaluate_opportunity_semantics(post)

    evaluation = evaluate_opportunity(
        signals=signals,
        engagement_potential=DEFAULT_ENGAGEMENT_POTENTIAL,
    )

    return {
        "opportunity_evaluation": evaluation,
    }
