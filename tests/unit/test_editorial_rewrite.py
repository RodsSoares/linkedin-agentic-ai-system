from unittest.mock import Mock, patch

import pytest

from app.schemas.editorial_preference import EditorialPreferenceEvaluation
from app.schemas.editorial_rewrite import EditorialRewriteInput
from app.schemas.scout import PostCandidate


def make_evaluation() -> EditorialPreferenceEvaluation:
    return EditorialPreferenceEvaluation(
        central_thesis_focus=92,
        contribution_density=88,
        conversational_naturalness=82,
        selective_evidence_use=100,
        stopping_discipline=86,
        front_loaded_value=72,
        synthetic_completeness_risk=36,
        publication_likelihood=78,
        core_thesis=(
            "Understand whether the process makes sense before automating it."
        ),
        must_preserve_elements=[
            "Process diagnosis before automation.",
        ],
        optional_support_elements=[
            "Compliance considerations.",
            "Flow-level metrics.",
        ],
        remove_or_compress_elements=[
            "Secondary explanatory detail after the thesis is already clear.",
        ],
        editorial_reason=(
            "Strong operational thesis, but secondary support should not be "
            "treated as mandatory and the central value should appear earlier."
        ),
        decision="ADJUST",
    )


def make_input() -> EditorialRewriteInput:
    return EditorialRewriteInput(
        source_post=PostCandidate(
            post_id="post-1",
            author_name="Test Author",
            post_text="Understand the process before automating it.",
            post_url="https://example.com/post-1",
            source="target_url",
        ),
        original_draft=(
            "There are several useful metrics to consider. "
            "Before automating, question whether the process should exist."
        ),
        editorial_evaluation=make_evaluation(),
        calibration_context=(
            "Prefer one central thesis, selective evidence, conversational "
            "professional language, strong stopping discipline, and front-loaded value."
        ),
    )


def parsed_result():
    from app.schemas.editorial_rewrite import EditorialRewriteResult

    return EditorialRewriteResult(
        revised_draft=(
            "Before automating, first ask whether the process still makes sense. "
            "Otherwise we may only execute a bad process faster."
        ),
        preserved_elements=[
            "Process diagnosis before automation.",
        ],
        removed_or_compressed_elements=[
            "Secondary metrics and explanatory detail.",
        ],
        rewrite_reason=(
            "Moved the central contribution forward and removed optional support "
            "that was not required for the thesis."
        ),
    )


@patch("app.components.editorial_rewrite.record_openai_usage")
@patch("app.components.editorial_rewrite.client")
def test_rewrite_uses_structured_output(mock_client, mock_usage):
    from app.components.editorial_rewrite import (
        rewrite_with_editorial_preference,
    )
    from app.schemas.editorial_rewrite import EditorialRewriteResult

    response = Mock()
    response.output_parsed = parsed_result()
    mock_client.responses.parse.return_value = response

    result = rewrite_with_editorial_preference(make_input())

    assert result.revised_draft
    kwargs = mock_client.responses.parse.call_args.kwargs
    assert kwargs["text_format"] is EditorialRewriteResult
    assert "ORIGINAL DRAFT:" in kwargs["input"]
    assert "EDITORIAL PREFERENCE EVALUATION:" in kwargs["input"]
    assert "front_loaded_value" in kwargs["input"]

    mock_usage.assert_called_once()


@patch("app.components.editorial_rewrite.record_openai_usage")
@patch("app.components.editorial_rewrite.client")
def test_rewrite_handles_missing_optional_context(mock_client, mock_usage):
    from app.components.editorial_rewrite import (
        rewrite_with_editorial_preference,
    )

    evaluation_input = make_input().model_copy(
        update={
            "research_result": None,
            "calibration_context": None,
        }
    )

    response = Mock()
    response.output_parsed = parsed_result()
    mock_client.responses.parse.return_value = response

    result = rewrite_with_editorial_preference(evaluation_input)

    assert result.revised_draft
    content = mock_client.responses.parse.call_args.kwargs["input"]
    assert "No research brief available." in content
    assert "No calibration context supplied." in content


@patch("app.components.editorial_rewrite.record_openai_usage")
@patch("app.components.editorial_rewrite.client")
def test_rewrite_passes_editorial_evaluation_without_mutating_it(
    mock_client,
    mock_usage,
):
    from app.components.editorial_rewrite import (
        rewrite_with_editorial_preference,
    )

    evaluation_input = make_input()
    before = evaluation_input.editorial_evaluation.model_dump()

    response = Mock()
    response.output_parsed = parsed_result()
    mock_client.responses.parse.return_value = response

    rewrite_with_editorial_preference(evaluation_input)

    assert evaluation_input.editorial_evaluation.model_dump() == before


@patch("app.components.editorial_rewrite.record_openai_usage")
@patch("app.components.editorial_rewrite.client")
def test_rewrite_rejects_missing_parsed_output(mock_client, mock_usage):
    from app.components.editorial_rewrite import (
        rewrite_with_editorial_preference,
    )

    response = Mock()
    response.output_parsed = None
    mock_client.responses.parse.return_value = response

    with pytest.raises(RuntimeError, match="returned no structured output"):
        rewrite_with_editorial_preference(make_input())
