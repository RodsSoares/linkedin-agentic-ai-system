import pytest

from unittest.mock import Mock, patch
from app.schemas.research import EvidenceItem
from app.components.perspective_generation import build_perspective_set

from app.schemas.argument import (
    ArgumentBrief,
    PerspectiveSetSynthesis,
    PerspectiveSynthesis,
)



def _make_evidence(
    claim: str,
    source_url: str,
) -> EvidenceItem:
    return EvidenceItem(
        claim=claim,
        support=f"Support for {claim}",
        source_url=source_url,
        source_title=f"Source for {claim}",
        relevance=90,
        confidence=90,
    )


def _make_argument_brief() -> ArgumentBrief:
    evidence_a = _make_evidence(
        claim="Agentic systems can coordinate specialized capabilities.",
        source_url="https://example.com/a",
    )
    evidence_b = _make_evidence(
        claim="Human oversight matters for consequential decisions.",
        source_url="https://example.com/b",
    )
    evidence_c = _make_evidence(
        claim="Operational value depends on process integration.",
        source_url="https://example.com/c",
    )

    return ArgumentBrief(
        original_thesis=(
            "AI-agent value depends on orchestration, process integration, "
            "and appropriately bounded human oversight."
        ),
        relevant_context=[
            "The discussion concerns multi-step business workflows."
        ],
        strongest_evidence=[
            evidence_a,
            evidence_b,
            evidence_c,
        ],
        strongest_counterevidence=[
            evidence_b,
        ],
        central_tensions=[
            "Automation speed versus human oversight."
        ],
        uncertainties=[
            "Mandatory approval thresholds are not established."
        ],
        contribution_areas=[
            "Operating-model design.",
            "Risk-based autonomy.",
        ],
    )


def _make_synthesis(
    first_indices: list[int] | None = None,
    second_indices: list[int] | None = None,
) -> PerspectiveSetSynthesis:
    return PerspectiveSetSynthesis(
        perspectives=[
            PerspectiveSynthesis(
                perspective_id="operating-model",
                label="Operating model",
                core_argument=(
                    "AI-agent value depends on operating-model design."
                ),
                why_it_matters=(
                    "Technical capability alone does not guarantee "
                    "operational value."
                ),
                supporting_evidence_indices=(
                    first_indices
                    if first_indices is not None
                    else [0, 2]
                ),
                counterargument=(
                    "Process redesign can increase implementation cost."
                ),
                uncertainty=None,
                contribution=(
                    "Shift attention from agent capability to "
                    "operational integration."
                ),
            ),
            PerspectiveSynthesis(
                perspective_id="bounded-autonomy",
                label="Bounded autonomy",
                core_argument=(
                    "Autonomy should depend on decision risk "
                    "and reversibility."
                ),
                why_it_matters=(
                    "Uniform approval policies can create either risk "
                    "or unnecessary friction."
                ),
                supporting_evidence_indices=(
                    second_indices
                    if second_indices is not None
                    else [1]
                ),
                counterargument=(
                    "Human checkpoints can reduce automation speed."
                ),
                uncertainty=(
                    "The appropriate approval thresholds are unclear."
                ),
                contribution=(
                    "Use decision characteristics to define "
                    "autonomy boundaries."
                ),
            ),
        ]
    )


def test_build_perspective_set_resolves_original_evidence():
    argument_brief = _make_argument_brief()
    synthesis = _make_synthesis()

    result = build_perspective_set(
        argument_brief=argument_brief,
        synthesis=synthesis,
    )

    assert len(result.perspectives) == 2

    assert result.perspectives[0].supporting_evidence == [
        argument_brief.strongest_evidence[0],
        argument_brief.strongest_evidence[2],
    ]

    assert result.perspectives[1].supporting_evidence == [
        argument_brief.strongest_evidence[1],
    ]


def test_build_perspective_set_preserves_semantic_fields():
    argument_brief = _make_argument_brief()
    synthesis = _make_synthesis()

    result = build_perspective_set(
        argument_brief=argument_brief,
        synthesis=synthesis,
    )

    perspective = result.perspectives[0]

    assert perspective.perspective_id == "operating-model"
    assert perspective.label == "Operating model"
    assert (
        perspective.core_argument
        == "AI-agent value depends on operating-model design."
    )
    assert (
        perspective.contribution
        == (
            "Shift attention from agent capability to "
            "operational integration."
        )
    )


def test_build_perspective_set_deduplicates_evidence_pool():
    argument_brief = _make_argument_brief()

    # evidence_b exists in both strongest_evidence and
    # strongest_counterevidence. It must appear only once in the pool.
    synthesis = _make_synthesis(
        first_indices=[1],
        second_indices=[1],
    )

    result = build_perspective_set(
        argument_brief=argument_brief,
        synthesis=synthesis,
    )

    expected_evidence = argument_brief.strongest_evidence[1]

    assert result.perspectives[0].supporting_evidence == [
        expected_evidence
    ]
    assert result.perspectives[1].supporting_evidence == [
        expected_evidence
    ]


def test_build_perspective_set_allows_empty_evidence_selection():
    argument_brief = _make_argument_brief()
    synthesis = _make_synthesis(
        first_indices=[],
        second_indices=[],
    )

    result = build_perspective_set(
        argument_brief=argument_brief,
        synthesis=synthesis,
    )

    assert result.perspectives[0].supporting_evidence == []
    assert result.perspectives[1].supporting_evidence == []


def test_build_perspective_set_rejects_out_of_range_index():
    argument_brief = _make_argument_brief()
    synthesis = _make_synthesis(
        first_indices=[99],
    )

    with pytest.raises(
        ValueError,
        match="invalid evidence index",
    ):
        build_perspective_set(
            argument_brief=argument_brief,
            synthesis=synthesis,
        )


def test_build_perspective_set_rejects_negative_index():
    argument_brief = _make_argument_brief()
    synthesis = _make_synthesis(
        first_indices=[-1],
    )

    with pytest.raises(
        ValueError,
        match="invalid evidence index",
    ):
        build_perspective_set(
            argument_brief=argument_brief,
            synthesis=synthesis,
        )


def test_build_perspective_set_rejects_duplicate_evidence_indices():
    argument_brief = _make_argument_brief()
    synthesis = _make_synthesis(
        first_indices=[0, 0],
    )

    with pytest.raises(
        ValueError,
        match="duplicate evidence indices",
    ):
        build_perspective_set(
            argument_brief=argument_brief,
            synthesis=synthesis,
        )


def test_build_perspective_set_rejects_duplicate_perspective_ids():
    argument_brief = _make_argument_brief()

    synthesis = PerspectiveSetSynthesis(
        perspectives=[
            PerspectiveSynthesis(
                perspective_id="same-id",
                label="Perspective A",
                core_argument="Argument A.",
                why_it_matters="Reason A.",
                contribution="Contribution A.",
            ),
            PerspectiveSynthesis(
                perspective_id="same-id",
                label="Perspective B",
                core_argument="Argument B.",
                why_it_matters="Reason B.",
                contribution="Contribution B.",
            ),
        ]
    )

    with pytest.raises(
        ValueError,
        match="duplicate perspective_id",
    ):
        build_perspective_set(
            argument_brief=argument_brief,
            synthesis=synthesis,
        )


def test_generate_perspective_set_uses_llm_synthesis_and_resolves_evidence():
    argument_brief = _make_argument_brief()

    synthesis = _make_synthesis(
        first_indices=[0, 2],
        second_indices=[1],
    )

    mock_response = Mock()
    mock_response.output_parsed = synthesis

    with (
        patch(
            "app.components.perspective_generation.client.responses.parse",
            return_value=mock_response,
        ) as mock_parse,
        patch(
            "app.components.perspective_generation.record_openai_usage"
        ) as mock_usage,
    ):
        from app.components.perspective_generation import (
            generate_perspective_set,
        )

        result = generate_perspective_set(argument_brief)

    assert len(result.perspectives) == 2

    assert result.perspectives[0].supporting_evidence == [
        argument_brief.strongest_evidence[0],
        argument_brief.strongest_evidence[2],
    ]

    assert result.perspectives[1].supporting_evidence == [
        argument_brief.strongest_evidence[1],
    ]

    mock_parse.assert_called_once()
    mock_usage.assert_called_once()


def test_generate_perspective_set_rejects_missing_structured_output():
    argument_brief = _make_argument_brief()

    mock_response = Mock()
    mock_response.output_parsed = None

    with (
        patch(
            "app.components.perspective_generation.client.responses.parse",
            return_value=mock_response,
        ),
        patch(
            "app.components.perspective_generation.record_openai_usage"
        ),
    ):
        from app.components.perspective_generation import (
            generate_perspective_set,
        )

        with pytest.raises(
            RuntimeError,
            match="returned no structured synthesis",
        ):
            generate_perspective_set(argument_brief)


def test_generate_perspective_set_rejects_invalid_llm_evidence_reference():
    argument_brief = _make_argument_brief()

    synthesis = _make_synthesis(
        first_indices=[99],
        second_indices=[1],
    )

    mock_response = Mock()
    mock_response.output_parsed = synthesis

    with (
        patch(
            "app.components.perspective_generation.client.responses.parse",
            return_value=mock_response,
        ),
        patch(
            "app.components.perspective_generation.record_openai_usage"
        ),
    ):
        from app.components.perspective_generation import (
            generate_perspective_set,
        )

        with pytest.raises(
            ValueError,
            match="invalid evidence index",
        ):
            generate_perspective_set(argument_brief)