import pytest
from pydantic import ValidationError
from unittest.mock import MagicMock, patch
from app.components.opportunity_evaluator import (
    evaluate_opportunity_semantics,
)
from app.schemas.post import PostCandidate

from app.components.opportunity_scoring import (
    calculate_opportunity_score,
    calculate_research_efficiency,
    classify_opportunity,
    evaluate_opportunity,
    has_low_opportunity_guardrail,
)
from app.schemas.opportunity import (
    OpportunityEvaluation,
    OpportunitySignals,
)


def test_opportunity_signals_accept_valid_scores():
    signals = OpportunitySignals(
        topic_relevance=80,
        positioning_fit=75,
        contribution_potential=90,
        research_cost=40,
    )

    assert signals.topic_relevance == 80
    assert signals.positioning_fit == 75
    assert signals.contribution_potential == 90
    assert signals.research_cost == 40


@pytest.mark.parametrize(
    "field",
    [
        "topic_relevance",
        "positioning_fit",
        "contribution_potential",
        "research_cost",
    ],
)
def test_opportunity_signals_reject_scores_below_zero(field):
    data = {
        "topic_relevance": 80,
        "positioning_fit": 75,
        "contribution_potential": 90,
        "research_cost": 40,
    }
    data[field] = -1

    with pytest.raises(ValidationError):
        OpportunitySignals(**data)


@pytest.mark.parametrize(
    "field",
    [
        "topic_relevance",
        "positioning_fit",
        "contribution_potential",
        "research_cost",
    ],
)
def test_opportunity_signals_reject_scores_above_100(field):
    data = {
        "topic_relevance": 80,
        "positioning_fit": 75,
        "contribution_potential": 90,
        "research_cost": 40,
    }
    data[field] = 101

    with pytest.raises(ValidationError):
        OpportunitySignals(**data)


def test_opportunity_evaluation_accepts_valid_result():
    evaluation = OpportunityEvaluation(
        topic_relevance=95,
        positioning_fit=95,
        contribution_potential=90,
        engagement_potential=80,
        research_cost=35,
        research_efficiency=65,
        opportunity_score=88.25,
        classification="HIGH",
    )

    assert evaluation.opportunity_score == 88.25
    assert evaluation.classification == "HIGH"


def test_opportunity_evaluation_rejects_invalid_classification():
    with pytest.raises(ValidationError):
        OpportunityEvaluation(
            topic_relevance=95,
            positioning_fit=95,
            contribution_potential=90,
            engagement_potential=80,
            research_cost=35,
            research_efficiency=65,
            opportunity_score=88.25,
            classification="VERY_HIGH",
        )


def test_calculate_research_efficiency():
    assert calculate_research_efficiency(0) == 100
    assert calculate_research_efficiency(50) == 50
    assert calculate_research_efficiency(100) == 0


def test_calculate_opportunity_score():
    signals = OpportunitySignals(
        topic_relevance=95,
        positioning_fit=95,
        contribution_potential=90,
        research_cost=35,
    )

    score = calculate_opportunity_score(
        signals=signals,
        engagement_potential=80,
    )

    assert score == 88.25


def test_guardrail_contribution_potential():
    signals = OpportunitySignals(
        topic_relevance=100,
        positioning_fit=100,
        contribution_potential=29,
        research_cost=0,
    )

    assert has_low_opportunity_guardrail(signals) is True


def test_guardrail_positioning_fit():
    signals = OpportunitySignals(
        topic_relevance=100,
        positioning_fit=29,
        contribution_potential=100,
        research_cost=0,
    )

    assert has_low_opportunity_guardrail(signals) is True


def test_guardrail_topic_relevance():
    signals = OpportunitySignals(
        topic_relevance=24,
        positioning_fit=100,
        contribution_potential=100,
        research_cost=0,
    )

    assert has_low_opportunity_guardrail(signals) is True


def test_guardrail_boundaries_do_not_trigger():
    signals = OpportunitySignals(
        topic_relevance=25,
        positioning_fit=30,
        contribution_potential=30,
        research_cost=50,
    )

    assert has_low_opportunity_guardrail(signals) is False


def test_classification_high():
    signals = OpportunitySignals(
        topic_relevance=90,
        positioning_fit=90,
        contribution_potential=90,
        research_cost=20,
    )

    assert classify_opportunity(signals, 80.0) == "HIGH"


def test_classification_medium():
    signals = OpportunitySignals(
        topic_relevance=70,
        positioning_fit=70,
        contribution_potential=70,
        research_cost=40,
    )

    assert classify_opportunity(signals, 60.0) == "MEDIUM"
    assert classify_opportunity(signals, 79.99) == "MEDIUM"


def test_classification_low():
    signals = OpportunitySignals(
        topic_relevance=60,
        positioning_fit=60,
        contribution_potential=60,
        research_cost=50,
    )

    assert classify_opportunity(signals, 59.99) == "LOW"


def test_guardrail_overrides_high_score():
    signals = OpportunitySignals(
        topic_relevance=100,
        positioning_fit=100,
        contribution_potential=29,
        research_cost=0,
    )

    assert classify_opportunity(signals, 95.0) == "LOW"


def test_evaluate_high_value_opportunity():
    signals = OpportunitySignals(
        topic_relevance=95,
        positioning_fit=95,
        contribution_potential=90,
        research_cost=35,
    )

    evaluation = evaluate_opportunity(
        signals=signals,
        engagement_potential=80,
    )

    assert evaluation.research_efficiency == 65
    assert evaluation.opportunity_score == 88.25
    assert evaluation.classification == "HIGH"

def test_evaluate_opportunity_semantics_returns_structured_signals():
    post = PostCandidate(
        post_id="test-post-001",
        post_url="https://www.linkedin.com/posts/test-post-001",
        author_name="Test Author",
        post_text="Generative AI can improve supply chain decision-making.",
    )

    expected_signals = OpportunitySignals(
        topic_relevance=95,
        positioning_fit=90,
        contribution_potential=85,
        research_cost=30,
    )

    mock_response = MagicMock()
    mock_response.output_parsed = expected_signals

    with patch(
        "app.components.opportunity_evaluator.client.responses.parse",
        return_value=mock_response,
    ) as mock_parse:
        result = evaluate_opportunity_semantics(post)

    assert result == expected_signals
    mock_parse.assert_called_once()

def test_evaluate_opportunity_semantics_raises_when_output_is_missing():
    post = PostCandidate(
        post_id="test-post-002",
        post_url="https://www.linkedin.com/posts/test-post-002",
        author_name="Test Author",
        post_text="A post about AI and business transformation.",
    )

    mock_response = MagicMock()
    mock_response.output_parsed = None

    with patch(
        "app.components.opportunity_evaluator.client.responses.parse",
        return_value=mock_response,
    ):
        with pytest.raises(
            RuntimeError,
            match="Opportunity semantic evaluation returned no structured output",
        ):
            evaluate_opportunity_semantics(post)