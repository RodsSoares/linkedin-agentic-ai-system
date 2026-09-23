from types import SimpleNamespace
from unittest.mock import patch

from app.graph.workflow import build_opportunity_workflow
from app.inputs.target_content import load_target_content
from app.schemas.opportunity import OpportunitySignals
from app.schemas.research import (
    ResearchBrief,
    ResearchObjective,
    ResearchStatus,
)


TARGET_URL = "https://www.linkedin.com/feed/update/urn:li:activity:123/"


def fake_reader(url: str) -> str:
    assert url == TARGET_URL
    return (
        "Before automating a process, understand why it exists, "
        "where the bottlenecks are, and what outcome should improve."
    )


def make_brief() -> ResearchBrief:
    return ResearchBrief(
        research_objective=ResearchObjective(
            question="What evidence supports this opportunity?",
            focus_areas=["process improvement", "automation"],
        ),
        summary="Research produced sufficient support.",
        key_findings=["One supported finding."],
        evidence=[],
        counterpoints=[],
        unresolved_questions=[],
        sources=[],
        status=ResearchStatus.SUFFICIENT,
    )


def fake_research_node(state):
    return {
        "research_result": make_brief(),
        "status": "RESEARCH_COMPLETED",
        "next_step": "writer",
    }


def fake_writer_node(state):
    iteration = state.get("iteration", 0) + 1
    return {
        "current_draft": f"Grounded target draft v{iteration}.",
        "iteration": iteration,
        "next_step": "evaluator",
        "status": "DRAFT_READY",
    }


def fake_evaluator_node(state):
    return {
        "quality_evaluation": SimpleNamespace(
            decision="PASS",
            revision_instruction=None,
        ),
        "next_step": "PASS",
        "status": "EVALUATED",
    }


def high_signals() -> OpportunitySignals:
    return OpportunitySignals(
        topic_relevance=95,
        positioning_fit=95,
        contribution_potential=90,
        research_cost=35,
    )


def test_target_content_enters_existing_opportunity_workflow():
    candidate = load_target_content(
        TARGET_URL,
        read_tool=fake_reader,
    )

    with (
        patch(
            "app.graph.nodes.opportunity_evaluator_node."
            "evaluate_opportunity_semantics",
            return_value=high_signals(),
        ),
        patch(
            "app.graph.workflow.research_node",
            side_effect=fake_research_node,
        ),
        patch(
            "app.graph.workflow.writer_node",
            side_effect=fake_writer_node,
        ),
        patch(
            "app.graph.workflow.evaluator_node",
            side_effect=fake_evaluator_node,
        ),
    ):
        workflow = build_opportunity_workflow()
        result = workflow.invoke({"post": candidate})

    assert result["post"] == candidate
    assert result["post"].source == "target_url"
    assert result["post"].post_url == TARGET_URL
    assert result["opportunity_evaluation"].classification == "HIGH"
    assert result["research_result"] == make_brief()
    assert result["current_draft"] == "Grounded target draft v1."
    assert result["quality_evaluation"].decision == "PASS"
    assert result["iteration"] == 1
    assert result["status"] == "EVALUATED"
    assert result["next_step"] == "PASS"
    