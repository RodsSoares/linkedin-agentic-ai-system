import pytest
from pydantic import ValidationError

from app.schemas.editorial_preference import (
    EditorialPreferenceEvaluation,
    EditorialPreferenceInput,
)
from app.schemas.scout import PostCandidate


def make_post() -> PostCandidate:
    return PostCandidate(
        post_id="post-1",
        author_name="Test Author",
        post_text="Understand the process before automating it.",
        post_url="https://example.com/post-1",
        source="target_url",
    )


def make_evaluation(**overrides) -> EditorialPreferenceEvaluation:
    data = {
        "central_thesis_focus": 90,
        "contribution_density": 88,
        "conversational_naturalness": 85,
        "selective_evidence_use": 92,
        "stopping_discipline": 84,
        "front_loaded_value": 86,
        "synthetic_completeness_risk": 30,
        "publication_likelihood": 80,
        "core_thesis": "Understand and improve the process before automating it.",
        "must_preserve_elements": [
            "Process diagnosis before automation.",
        ],
        "optional_support_elements": [
            "Flow-level metrics.",
            "Compliance considerations.",
        ],
        "remove_or_compress_elements": [
            "Redundant explanatory detail.",
        ],
        "editorial_reason": "Strong thesis with some optional supporting detail.",
        "decision": "PASS",
    }
    data.update(overrides)
    return EditorialPreferenceEvaluation(**data)


def test_input_accepts_valid_comment():
    result = EditorialPreferenceInput(
        source_post=make_post(),
        draft="A useful comment.",
        content_intent="COMMENT",
    )
    assert result.draft == "A useful comment."


def test_input_strips_draft():
    result = EditorialPreferenceInput(
        source_post=make_post(),
        draft="  A useful comment.  ",
    )
    assert result.draft == "A useful comment."


def test_input_rejects_empty_draft():
    with pytest.raises(ValidationError):
        EditorialPreferenceInput(
            source_post=make_post(),
            draft="   ",
        )


def test_input_rejects_unsupported_content_intent():
    with pytest.raises(ValidationError):
        EditorialPreferenceInput(
            source_post=make_post(),
            draft="A useful comment.",
            content_intent="AUTHORIAL_POST",
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "central_thesis_focus",
        "contribution_density",
        "conversational_naturalness",
        "selective_evidence_use",
        "stopping_discipline",
        "front_loaded_value",
        "synthetic_completeness_risk",
        "publication_likelihood",
    ],
)
@pytest.mark.parametrize("invalid_value", [-1, 101])
def test_scores_are_bounded(field_name, invalid_value):
    with pytest.raises(ValidationError):
        make_evaluation(**{field_name: invalid_value})


def test_decision_restricted():
    with pytest.raises(ValidationError):
        make_evaluation(decision="REJECT")


def test_adjust_is_valid():
    result = make_evaluation(decision="ADJUST")
    assert result.decision == "ADJUST"


def test_core_thesis_required():
    with pytest.raises(ValidationError):
        make_evaluation(core_thesis="")


@pytest.mark.parametrize(
    ("field_name", "limit"),
    [
        ("must_preserve_elements", 5),
        ("optional_support_elements", 8),
        ("remove_or_compress_elements", 8),
    ],
)
def test_editorial_lists_are_bounded(field_name, limit):
    values = [f"item-{index}" for index in range(limit + 1)]

    with pytest.raises(ValidationError):
        make_evaluation(**{field_name: values})


def test_support_can_be_optional_without_being_must_preserve():
    result = make_evaluation(
        must_preserve_elements=["Central process-before-automation thesis."],
        optional_support_elements=[
            "Compliance.",
            "Retrabalho.",
            "Qualidade na primeira execução.",
        ],
    )

    assert len(result.must_preserve_elements) == 1
    assert len(result.optional_support_elements) == 3
