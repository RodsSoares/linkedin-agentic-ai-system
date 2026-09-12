import pytest
from pydantic import ValidationError

from app.components.editorial_preference_evaluator import (
    evaluate_editorial_preference,
)
from app.schemas.editorial_preference import (
    EditorialPreferenceEvaluation,
    EditorialPreferenceInput,
)
from app.schemas.scout import PostCandidate


def make_input() -> EditorialPreferenceInput:
    return EditorialPreferenceInput(
        source_post=PostCandidate(
            post_id="post-1",
            author_name="Test Author",
            post_text="Understand the process before automating it.",
            post_url="https://example.com/post-1",
            source="target_url",
        ),
        draft="Before automating, understand whether the process makes sense.",
        calibration_context="Prefer one central thesis and selective support.",
    )


def make_evaluation() -> EditorialPreferenceEvaluation:
    return EditorialPreferenceEvaluation(
        central_thesis_focus=92,
        contribution_density=90,
        conversational_naturalness=88,
        selective_evidence_use=94,
        stopping_discipline=89,
        front_loaded_value=91,
        synthetic_completeness_risk=24,
        publication_likelihood=84,
        core_thesis="Understand the process before automating it.",
        must_preserve_elements=[
            "Process diagnosis before automation.",
        ],
        optional_support_elements=[
            "Flow metrics.",
        ],
        remove_or_compress_elements=[],
        editorial_reason="Strong central thesis with restrained support.",
        decision="PASS",
    )


def test_exact_input_is_passed_to_semantic_evaluator():
    evaluation_input = make_input()
    captured = {}

    def semantic_evaluator(value):
        captured["value"] = value
        return make_evaluation()

    evaluate_editorial_preference(
        evaluation_input,
        semantic_evaluator=semantic_evaluator,
    )

    assert captured["value"] is evaluation_input


def test_accepts_structured_model():
    result = evaluate_editorial_preference(
        make_input(),
        semantic_evaluator=lambda _: make_evaluation(),
    )

    assert isinstance(result, EditorialPreferenceEvaluation)
    assert result.front_loaded_value == 91


def test_mapping_is_validated():
    expected = make_evaluation()

    result = evaluate_editorial_preference(
        make_input(),
        semantic_evaluator=lambda _: expected.model_dump(),
    )

    assert result == expected


def test_invalid_score_is_rejected():
    invalid = make_evaluation().model_dump()
    invalid["front_loaded_value"] = 101

    with pytest.raises(ValidationError):
        evaluate_editorial_preference(
            make_input(),
            semantic_evaluator=lambda _: invalid,
        )


def test_invalid_decision_is_rejected():
    invalid = make_evaluation().model_dump()
    invalid["decision"] = "REJECT"

    with pytest.raises(ValidationError):
        evaluate_editorial_preference(
            make_input(),
            semantic_evaluator=lambda _: invalid,
        )


def test_adjust_is_not_failure():
    evaluation = make_evaluation().model_copy(update={"decision": "ADJUST"})

    result = evaluate_editorial_preference(
        make_input(),
        semantic_evaluator=lambda _: evaluation,
    )

    assert result.decision == "ADJUST"


def test_input_is_not_mutated():
    evaluation_input = make_input()
    before = evaluation_input.model_dump()

    evaluate_editorial_preference(
        evaluation_input,
        semantic_evaluator=lambda _: make_evaluation(),
    )

    assert evaluation_input.model_dump() == before
