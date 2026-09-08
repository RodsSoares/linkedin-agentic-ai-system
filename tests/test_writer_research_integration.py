from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.components.writer import format_research_context
from app.graph.nodes.writer_node import writer_node
from app.schemas.post import PostCandidate
from app.schemas.research import (
    EvidenceItem,
    ResearchBrief,
    ResearchObjective,
    ResearchStatus,
)
from app.schemas.writer import WriterInput


def make_post() -> PostCandidate:
    return PostCandidate(
        post_id="writer-research-001",
        author_name="Test Author",
        post_text="AI agents can support supply chain planning.",
        post_url="https://example.com/writer-research-001",
    )


def make_brief() -> ResearchBrief:
    return ResearchBrief(
        research_objective=ResearchObjective(
            question="What evidence supports this opportunity?",
            focus_areas=["agentic planning"],
        ),
        summary="Research found bounded support for the opportunity.",
        key_findings=["Agentic systems can support multi-step work."],
        evidence=[
            EvidenceItem(
                claim="Agentic systems can execute bounded multi-step work.",
                support="The observed source describes controlled tool use.",
                source_url="https://example.com/evidence",
                source_title="Evidence Source",
                relevance=95,
                confidence=90,
            )
        ],
        counterpoints=["Human oversight remains important."],
        unresolved_questions=["How should production metrics be calibrated?"],
        sources=[],
        status=ResearchStatus.SUFFICIENT,
    )


def test_writer_input_accepts_structured_research_brief():
    brief = make_brief()

    writer_input = WriterInput(
        post=make_post(),
        research_result=brief,
    )

    assert writer_input.research_result == brief


def test_writer_input_rejects_arbitrary_research_dict():
    with pytest.raises(ValidationError):
        WriterInput(
            post=make_post(),
            research_result={
                "unexpected": "unstructured placeholder",
            },
        )


def test_format_research_context_serializes_brief_explicitly():
    context = format_research_context(make_brief())

    assert '"summary"' in context
    assert '"key_findings"' in context
    assert '"evidence"' in context
    assert '"counterpoints"' in context
    assert '"unresolved_questions"' in context
    assert '"status": "SUFFICIENT"' in context


def test_format_research_context_handles_missing_research():
    assert (
        format_research_context(None)
        == "No research brief was provided."
    )


def test_writer_node_passes_exact_research_brief_to_writer():
    brief = make_brief()

    with patch(
        "app.graph.nodes.writer_node.writer",
        return_value="Grounded draft.",
    ) as writer_mock:
        result = writer_node(
            {
                "post": make_post(),
                "research_result": brief,
            }
        )

    writer_input = writer_mock.call_args.args[0]

    assert writer_input.research_result is brief
    assert result["current_draft"] == "Grounded draft."
    assert result["iteration"] == 1
    assert result["status"] == "DRAFT_READY"
    assert result["next_step"] == "evaluator"
