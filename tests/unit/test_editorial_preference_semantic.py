from unittest.mock import Mock, patch

import pytest

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
        calibration_context="Prefer one central thesis and selective evidence.",
    )


def make_evaluation() -> EditorialPreferenceEvaluation:
    return EditorialPreferenceEvaluation(
        central_thesis_focus=93,
        contribution_density=90,
        conversational_naturalness=87,
        selective_evidence_use=95,
        stopping_discipline=88,
        front_loaded_value=90,
        synthetic_completeness_risk=28,
        publication_likelihood=83,
        core_thesis="Understand the process before automating it.",
        must_preserve_elements=[
            "Process diagnosis before automation.",
        ],
        optional_support_elements=[
            "Flow-level metrics.",
        ],
        remove_or_compress_elements=[],
        editorial_reason="Strong thesis with optional support kept separate.",
        decision="PASS",
    )


@patch("app.components.editorial_preference_semantic.record_openai_usage")
@patch("app.components.editorial_preference_semantic.client")
def test_semantic_evaluation_returns_structured_output(mock_client, mock_usage):
    from app.components.editorial_preference_semantic import (
        evaluate_editorial_preference_semantics,
    )

    response = Mock()
    response.output_parsed = make_evaluation()
    mock_client.responses.parse.return_value = response

    result = evaluate_editorial_preference_semantics(make_input())

    assert isinstance(result, EditorialPreferenceEvaluation)
    assert result.front_loaded_value == 90


@patch("app.components.editorial_preference_semantic.record_openai_usage")
@patch("app.components.editorial_preference_semantic.client")
def test_input_contains_source_draft_and_calibration(mock_client, mock_usage):
    from app.components.editorial_preference_semantic import (
        evaluate_editorial_preference_semantics,
    )

    response = Mock()
    response.output_parsed = make_evaluation()
    mock_client.responses.parse.return_value = response

    evaluate_editorial_preference_semantics(make_input())

    content = mock_client.responses.parse.call_args.kwargs["input"]
    assert "Understand the process before automating it." in content
    assert "Before automating, understand whether the process makes sense." in content
    assert "Prefer one central thesis and selective evidence." in content


@patch("app.components.editorial_preference_semantic.record_openai_usage")
@patch("app.components.editorial_preference_semantic.client")
def test_missing_optional_context_is_handled(mock_client, mock_usage):
    from app.components.editorial_preference_semantic import (
        evaluate_editorial_preference_semantics,
    )

    evaluation_input = make_input().model_copy(
        update={
            "research_result": None,
            "calibration_context": None,
        }
    )

    response = Mock()
    response.output_parsed = make_evaluation()
    mock_client.responses.parse.return_value = response

    evaluate_editorial_preference_semantics(evaluation_input)

    content = mock_client.responses.parse.call_args.kwargs["input"]
    assert "No research brief available." in content
    assert "No calibration context supplied." in content


@patch("app.components.editorial_preference_semantic.record_openai_usage")
@patch("app.components.editorial_preference_semantic.client")
def test_usage_is_recorded(mock_client, mock_usage):
    from app.components.editorial_preference_semantic import (
        evaluate_editorial_preference_semantics,
    )

    response = Mock()
    response.output_parsed = make_evaluation()
    mock_client.responses.parse.return_value = response

    evaluate_editorial_preference_semantics(make_input())

    usage_kwargs = mock_usage.call_args.kwargs
    assert usage_kwargs["component"] == "editorial_preference"
    assert usage_kwargs["operation"] == "evaluate"
    assert usage_kwargs["response"] is response


@patch("app.components.editorial_preference_semantic.record_openai_usage")
@patch("app.components.editorial_preference_semantic.client")
def test_missing_parsed_output_raises(mock_client, mock_usage):
    from app.components.editorial_preference_semantic import (
        evaluate_editorial_preference_semantics,
    )

    response = Mock()
    response.output_parsed = None
    mock_client.responses.parse.return_value = response

    with pytest.raises(RuntimeError, match="returned no structured output"):
        evaluate_editorial_preference_semantics(make_input())
