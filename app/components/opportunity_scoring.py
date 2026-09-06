from app.schemas.opportunity import OpportunityEvaluation, OpportunitySignals


CONTRIBUTION_WEIGHT = 0.30
POSITIONING_WEIGHT = 0.25
TOPIC_WEIGHT = 0.20
ENGAGEMENT_WEIGHT = 0.15
RESEARCH_EFFICIENCY_WEIGHT = 0.10


def calculate_research_efficiency(research_cost: int) -> int:
    return 100 - research_cost


def calculate_opportunity_score(
    signals: OpportunitySignals,
    engagement_potential: int,
) -> float:
    research_efficiency = calculate_research_efficiency(signals.research_cost)

    score = (
        signals.contribution_potential * CONTRIBUTION_WEIGHT
        + signals.positioning_fit * POSITIONING_WEIGHT
        + signals.topic_relevance * TOPIC_WEIGHT
        + engagement_potential * ENGAGEMENT_WEIGHT
        + research_efficiency * RESEARCH_EFFICIENCY_WEIGHT
    )

    return round(score, 2)


def has_low_opportunity_guardrail(signals: OpportunitySignals) -> bool:
    return (
        signals.contribution_potential < 30
        or signals.positioning_fit < 30
        or signals.topic_relevance < 25
    )


def classify_opportunity(
    signals: OpportunitySignals,
    opportunity_score: float,
) -> str:
    if has_low_opportunity_guardrail(signals):
        return "LOW"

    if opportunity_score >= 80:
        return "HIGH"

    if opportunity_score >= 60:
        return "MEDIUM"

    return "LOW"


def evaluate_opportunity(
    signals: OpportunitySignals,
    engagement_potential: int,
) -> OpportunityEvaluation:
    research_efficiency = calculate_research_efficiency(signals.research_cost)

    opportunity_score = calculate_opportunity_score(
        signals=signals,
        engagement_potential=engagement_potential,
    )

    classification = classify_opportunity(
        signals=signals,
        opportunity_score=opportunity_score,
    )

    return OpportunityEvaluation(
        topic_relevance=signals.topic_relevance,
        positioning_fit=signals.positioning_fit,
        contribution_potential=signals.contribution_potential,
        engagement_potential=engagement_potential,
        research_cost=signals.research_cost,
        research_efficiency=research_efficiency,
        opportunity_score=opportunity_score,
        classification=classification,
    )