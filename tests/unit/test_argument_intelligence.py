import pytest

from unittest.mock import Mock, patch
from app.components.argument_intelligence import build_argument_brief
from app.schemas.argument import ArgumentSynthesis

from app.schemas.research import (
    EvidenceItem,
    ResearchBrief,
    ResearchObjective,
    ResearchStatus,
)


def make_evidence(
    claim: str,
    source_url: str,
) -> EvidenceItem:
    return EvidenceItem(
        claim=claim,
        support=f"Support for: {claim}",
        source_url=source_url,
        source_title=f"Source for {claim}",
        relevance=90,
        confidence=85,
    )


def make_research_brief() -> ResearchBrief:
    return ResearchBrief(
        research_objective=ResearchObjective(
            question="How is AI changing professional work?",
            focus_areas=[
                "Operational impact",
                "Organizational impact",
            ],
        ),
        summary="AI is changing how professional work is organized.",
        key_findings=[
            "AI can reduce manual analytical work.",
            "Organizational redesign affects realized value.",
            "Implementation quality constrains outcomes.",
        ],
        evidence=[
            make_evidence(
                claim="AI can reduce manual analytical work.",
                source_url="https://example.com/source-1",
            ),
            make_evidence(
                claim="Organizational redesign affects realized value.",
                source_url="https://example.com/source-2",
            ),
            make_evidence(
                claim="Implementation quality constrains outcomes.",
                source_url="https://example.com/source-3",
            ),
        ],
        counterpoints=[
            "Technology adoption alone does not guarantee productivity gains.",
        ],
        unresolved_questions=[
            "How durable are the observed productivity effects?",
        ],
        sources=[],
        status=ResearchStatus.SUFFICIENT,
    )


def make_synthesis(
    strongest_evidence_indices: list[int] | None = None,
    strongest_counterevidence_indices: list[int] | None = None,
) -> ArgumentSynthesis:
    return ArgumentSynthesis(
        original_thesis="AI will substantially change professional work.",
        relevant_context=[
            "The impact depends on more than technology adoption alone.",
        ],
        strongest_evidence_indices=(
            strongest_evidence_indices
            if strongest_evidence_indices is not None
            else [0, 1]
        ),
        strongest_counterevidence_indices=(
            strongest_counterevidence_indices
            if strongest_counterevidence_indices is not None
            else [2]
        ),
        central_tensions=[
            "Automation efficiency versus organizational redesign.",
        ],
        uncertainties=[
            "Long-term productivity effects remain uncertain.",
        ],
        contribution_areas=[
            "Connect AI adoption with operating-model change.",
        ],
    )


def test_build_argument_brief_resolves_original_evidence_items():
    research_brief = make_research_brief()
    synthesis = make_synthesis()

    argument_brief = build_argument_brief(
        research_brief=research_brief,
        synthesis=synthesis,
    )

    assert argument_brief.strongest_evidence == [
        research_brief.evidence[0],
        research_brief.evidence[1],
    ]
    assert argument_brief.strongest_counterevidence == [
        research_brief.evidence[2],
    ]


def test_build_argument_brief_preserves_semantic_synthesis():
    research_brief = make_research_brief()
    synthesis = make_synthesis()

    argument_brief = build_argument_brief(
        research_brief=research_brief,
        synthesis=synthesis,
    )

    assert argument_brief.original_thesis == synthesis.original_thesis
    assert argument_brief.relevant_context == synthesis.relevant_context
    assert argument_brief.central_tensions == synthesis.central_tensions
    assert argument_brief.uncertainties == synthesis.uncertainties
    assert argument_brief.contribution_areas == synthesis.contribution_areas


def test_build_argument_brief_allows_empty_evidence_selection():
    research_brief = make_research_brief()
    synthesis = make_synthesis(
        strongest_evidence_indices=[],
        strongest_counterevidence_indices=[],
    )

    argument_brief = build_argument_brief(
        research_brief=research_brief,
        synthesis=synthesis,
    )

    assert argument_brief.strongest_evidence == []
    assert argument_brief.strongest_counterevidence == []


def test_build_argument_brief_rejects_out_of_range_evidence_index():
    research_brief = make_research_brief()
    synthesis = make_synthesis(
        strongest_evidence_indices=[3],
    )

    with pytest.raises(
        ValueError,
        match="strongest_evidence_indices contains invalid evidence index 3",
    ):
        build_argument_brief(
            research_brief=research_brief,
            synthesis=synthesis,
        )


def test_build_argument_brief_rejects_negative_evidence_index():
    research_brief = make_research_brief()
    synthesis = make_synthesis(
        strongest_evidence_indices=[-1],
    )

    with pytest.raises(
        ValueError,
        match="strongest_evidence_indices contains invalid evidence index -1",
    ):
        build_argument_brief(
            research_brief=research_brief,
            synthesis=synthesis,
        )


def test_build_argument_brief_rejects_duplicate_evidence_indices():
    research_brief = make_research_brief()
    synthesis = make_synthesis(
        strongest_evidence_indices=[0, 0],
    )

    with pytest.raises(
        ValueError,
        match="strongest_evidence_indices contains duplicate evidence indices",
    ):
        build_argument_brief(
            research_brief=research_brief,
            synthesis=synthesis,
        )


def test_build_argument_brief_rejects_invalid_counterevidence_index():
    research_brief = make_research_brief()
    synthesis = make_synthesis(
        strongest_counterevidence_indices=[99],
    )

    with pytest.raises(
        ValueError,
        match=(
            "strongest_counterevidence_indices contains "
            "invalid evidence index 99"
        ),
    ):
        build_argument_brief(
            research_brief=research_brief,
            synthesis=synthesis,
        )


def test_build_argument_brief_rejects_duplicate_counterevidence_indices():
    research_brief = make_research_brief()
    synthesis = make_synthesis(
        strongest_counterevidence_indices=[1, 1],
    )

    with pytest.raises(
        ValueError,
        match=(
            "strongest_counterevidence_indices contains "
            "duplicate evidence indices"
        ),
    ):
        build_argument_brief(
            research_brief=research_brief,
            synthesis=synthesis,
        )


def test_generate_argument_brief_uses_structured_llm_output():
    from app.components.argument_intelligence import generate_argument_brief

    research_brief = make_research_brief()
    synthesis = make_synthesis(
        strongest_evidence_indices=[0, 1],
        strongest_counterevidence_indices=[2],
    )

    mock_response = Mock()
    mock_response.output_parsed = synthesis

    with (
        patch(
            "app.components.argument_intelligence.client.responses.parse",
            return_value=mock_response,
        ) as mock_parse,
        patch(
            "app.components.argument_intelligence.record_openai_usage"
        ) as mock_record_usage,
    ):
        argument_brief = generate_argument_brief(research_brief)

    mock_parse.assert_called_once()
    mock_record_usage.assert_called_once()

    assert argument_brief.original_thesis == synthesis.original_thesis
    assert argument_brief.strongest_evidence == [
        research_brief.evidence[0],
        research_brief.evidence[1],
    ]
    assert argument_brief.strongest_counterevidence == [
        research_brief.evidence[2],
    ]


def test_generate_argument_brief_rejects_missing_structured_output():
    from app.components.argument_intelligence import generate_argument_brief

    research_brief = make_research_brief()

    mock_response = Mock()
    mock_response.output_parsed = None

    with (
        patch(
            "app.components.argument_intelligence.client.responses.parse",
            return_value=mock_response,
        ),
        patch(
            "app.components.argument_intelligence.record_openai_usage"
        ),
        pytest.raises(
            RuntimeError,
            match="Argument Intelligence returned no structured synthesis",
        ),
    ):
        generate_argument_brief(research_brief)


def test_generate_argument_brief_rejects_invalid_llm_evidence_reference():
    from app.components.argument_intelligence import generate_argument_brief

    research_brief = make_research_brief()
    synthesis = make_synthesis(
        strongest_evidence_indices=[99],
    )

    mock_response = Mock()
    mock_response.output_parsed = synthesis

    with (
        patch(
            "app.components.argument_intelligence.client.responses.parse",
            return_value=mock_response,
        ),
        patch(
            "app.components.argument_intelligence.record_openai_usage"
        ),
        pytest.raises(
            ValueError,
            match="strongest_evidence_indices contains invalid evidence index 99",
        ),
    ):
        generate_argument_brief(research_brief)