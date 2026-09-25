from types import SimpleNamespace
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.components.writer import (
    format_research_context,
    format_selected_perspective,
    writer,
)
from app.graph.nodes.writer_node import writer_node
from app.schemas.argument import Perspective, SelectedPerspective
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
        unresolved_questions=[
            "How should production metrics be calibrated?"
        ],
        sources=[],
        status=ResearchStatus.SUFFICIENT,
    )


def make_selected_perspective() -> SelectedPerspective:
    return SelectedPerspective(
        perspective=Perspective(
            perspective_id="risk-calibrated-autonomy",
            label="Risk-calibrated autonomy",
            core_argument=(
                "Agent autonomy should depend on decision risk "
                "and reversibility."
            ),
            why_it_matters=(
                "Different decisions justify different levels "
                "of human control."
            ),
            supporting_evidence=[
                make_brief().evidence[0]
            ],
            counterargument=(
                "Risk and reversibility can be difficult to assess."
            ),
            uncertainty=(
                "No universal threshold is available."
            ),
            contribution=(
                "Move beyond the binary choice between full automation "
                "and universal human approval."
            ),
        ),
        human_guidance=(
            "Keep the argument practical and avoid sounding absolute."
        ),
    )


def test_writer_input_accepts_structured_research_brief():
    brief = make_brief()

    writer_input = WriterInput(
        post=make_post(),
        research_result=brief,
    )

    assert writer_input.research_result == brief


def test_writer_input_accepts_selected_perspective():
    selected_perspective = make_selected_perspective()

    writer_input = WriterInput(
        post=make_post(),
        selected_perspective=selected_perspective,
    )

    assert writer_input.selected_perspective == selected_perspective


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


def test_format_selected_perspective_serializes_selection_explicitly():
    context = format_selected_perspective(
        make_selected_perspective()
    )

    assert '"perspective_id": "risk-calibrated-autonomy"' in context
    assert '"core_argument"' in context
    assert '"supporting_evidence"' in context
    assert '"counterargument"' in context
    assert '"uncertainty"' in context
    assert '"contribution"' in context
    assert '"human_guidance"' in context
    assert (
        "Keep the argument practical and avoid sounding absolute."
        in context
    )


def test_format_selected_perspective_handles_missing_selection():
    assert (
        format_selected_perspective(None)
        == "No human-selected perspective was provided."
    )


def test_writer_sends_research_and_selected_perspective_to_llm():
    brief = make_brief()
    selected_perspective = make_selected_perspective()

    response = SimpleNamespace(
        output_text="Grounded perspective-aware draft."
    )

    with (
        patch(
            "app.components.writer.client.responses.create",
            return_value=response,
        ) as create_mock,
        patch(
            "app.components.writer.record_openai_usage"
        ),
    ):
        result = writer(
            WriterInput(
                post=make_post(),
                research_result=brief,
                selected_perspective=selected_perspective,
            )
        )

    user_content = create_mock.call_args.kwargs["input"]

    assert "RESEARCH BRIEF:" in user_content
    assert "HUMAN-SELECTED PERSPECTIVE:" in user_content
    assert "Research found bounded support" in user_content
    assert "risk-calibrated-autonomy" in user_content
    assert (
        "Agent autonomy should depend on decision risk "
        "and reversibility."
        in user_content
    )
    assert (
        "Keep the argument practical and avoid sounding absolute."
        in user_content
    )
    assert result == "Grounded perspective-aware draft."


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


def test_writer_node_passes_exact_selected_perspective_to_writer():
    selected_perspective = make_selected_perspective()

    state = {
        "post": make_post(),
        "research_result": make_brief(),
        "selected_perspective": selected_perspective,
        "current_draft": None,
        "quality_evaluation": None,
        "iteration": 0,
    }

    with patch(
        "app.graph.nodes.writer_node.writer",
        return_value="Perspective-aware draft.",
    ) as writer_mock:
        result = writer_node(state)

    writer_input = writer_mock.call_args.args[0]

    assert writer_input.selected_perspective is selected_perspective
    assert result["current_draft"] == "Perspective-aware draft."
