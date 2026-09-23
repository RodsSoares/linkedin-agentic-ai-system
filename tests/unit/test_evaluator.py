from app.components.evaluator import (
    calculate_voice_match,
    determine_decision,
)
from app.schemas.evaluator import (
    EvaluationSignals,
    EvaluatorInput,
    VoiceEvaluation,
)
from app.schemas.post import PostCandidate
from app.schemas.research import (
    ResearchBrief,
    ResearchObjective,
    ResearchStatus,
)

def make_signals(
    naturalness=80,
    directness=80,
    practical_insight=80,
    professional_maturity=80,
    business_technology_fit=80,
    anti_cliche=80,
    non_promotional=80,
    factual_accuracy=100,
    relevance=100,
):
    return EvaluationSignals(
        factual_accuracy=factual_accuracy,
        relevance=relevance,
        voice=VoiceEvaluation(
            naturalness=naturalness,
            directness=directness,
            practical_insight=practical_insight,
            professional_maturity=professional_maturity,
            business_technology_fit=business_technology_fit,
            anti_cliche=anti_cliche,
            non_promotional=non_promotional,
        ),
        revision_instruction=None,
    )


def test_calculate_voice_match_uses_average():
    signals = make_signals(
        naturalness=70,
        directness=80,
        practical_insight=90,
        professional_maturity=100,
        business_technology_fit=80,
        anti_cliche=90,
        non_promotional=70,
    )

    result = calculate_voice_match(signals)

    assert result == 83


def test_determine_decision_passes_when_all_thresholds_are_met():
    result = determine_decision(
        factual_accuracy=90,
        relevance=80,
        voice_match=75,
    )

    assert result == "PASS"


def test_determine_decision_revises_when_voice_is_below_pass_threshold():
    result = determine_decision(
        factual_accuracy=95,
        relevance=90,
        voice_match=74,
    )

    assert result == "REVISE"


def test_determine_decision_revises_when_relevance_is_in_intermediate_zone():
    result = determine_decision(
        factual_accuracy=95,
        relevance=70,
        voice_match=90,
    )

    assert result == "REVISE"


def test_determine_decision_rejects_low_factual_accuracy():
    result = determine_decision(
        factual_accuracy=49,
        relevance=100,
        voice_match=100,
    )

    assert result == "REJECT"


def test_determine_decision_rejects_low_relevance():
    result = determine_decision(
        factual_accuracy=100,
        relevance=39,
        voice_match=100,
    )

    assert result == "REJECT"


def test_evaluator_input_accepts_typed_research_brief():
    research_brief = ResearchBrief(
        research_objective=ResearchObjective(
            question="What controls are required for bounded AI autonomy?",
        ),
        summary="Bounded autonomy requires explicit authorization and escalation rules.",
        status=ResearchStatus.SUFFICIENT,
    )

    post = PostCandidate(
        post_id="test-post-001",
        author_name="Test Author",
        post_text="A test post about bounded AI autonomy.",
        post_url="https://example.com/test-post",
        source="test",
    )

    evaluator_input = EvaluatorInput(
        post=post,
        current_draft="A test draft grounded in the research brief.",
        research_result=research_brief,
    )

    assert evaluator_input.research_result is research_brief
    assert isinstance(evaluator_input.research_result, ResearchBrief)
    assert evaluator_input.research_result.status == ResearchStatus.SUFFICIENT