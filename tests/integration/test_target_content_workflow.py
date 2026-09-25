from unittest.mock import patch

from langgraph.types import Command

from app.graph.workflow import build_opportunity_workflow
from app.inputs.target_content import load_target_content
from app.schemas.argument import (
    ArgumentBrief,
    Perspective,
    PerspectiveSet,
)
from app.schemas.evaluator import QualityEvaluation
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


def make_argument_brief() -> ArgumentBrief:
    return ArgumentBrief(
        original_thesis=(
            "Before automating a process, understand why it exists."
        ),
        relevant_context=[],
        strongest_evidence=[],
        strongest_counterevidence=[],
        central_tensions=[],
        uncertainties=[],
        contribution_areas=[
            "Process understanding before automation",
            "Outcome-oriented automation",
        ],
    )


def make_perspective_set() -> PerspectiveSet:
    return PerspectiveSet(
        perspectives=[
            Perspective(
                perspective_id="process-first",
                label="Process first",
                core_argument=(
                    "Automation should follow process understanding."
                ),
                why_it_matters=(
                    "Automating an unclear process can preserve "
                    "or amplify its problems."
                ),
                supporting_evidence=[],
                counterargument=None,
                uncertainty=None,
                contribution=(
                    "Prioritize process diagnosis before automation."
                ),
            ),
            Perspective(
                perspective_id="outcome-first",
                label="Outcome first",
                core_argument=(
                    "Automation should begin with the outcome "
                    "that needs to improve."
                ),
                why_it_matters=(
                    "Technology should be connected to a measurable "
                    "operational objective."
                ),
                supporting_evidence=[],
                counterargument=None,
                uncertainty=None,
                contribution=(
                    "Frame automation around operational outcomes."
                ),
            ),
        ]
    )


def fake_research_node(state):
    return {
        "research_result": make_brief(),
        "status": "RESEARCH_COMPLETED",
        "next_step": "argument_intelligence",
    }


def fake_argument_intelligence_node(state):
    assert state["research_result"] == make_brief()

    return {
        "argument_brief": make_argument_brief(),
    }


def fake_perspective_generation_node(state):
    assert state["argument_brief"] == make_argument_brief()

    return {
        "perspective_set": make_perspective_set(),
    }


def fake_writer_node(state):
    assert state["selected_perspective"] is not None

    iteration = state.get("iteration", 0) + 1

    return {
        "current_draft": f"Grounded target draft v{iteration}.",
        "iteration": iteration,
        "next_step": "evaluator",
        "status": "DRAFT_READY",
    }


def fake_evaluator_node(state):
    return {
        "quality_evaluation": QualityEvaluation(
            factual_accuracy=100,
            relevance=100,
            voice_match=100,
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
            "app.graph.workflow.argument_intelligence_node",
            side_effect=fake_argument_intelligence_node,
        ),
        patch(
            "app.graph.workflow.perspective_generation_node",
            side_effect=fake_perspective_generation_node,
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

        config = {
            "configurable": {
                "thread_id": "target-content-human-centered",
            }
        }

        interrupted = workflow.invoke(
            {"post": candidate},
            config=config,
        )

        assert "__interrupt__" in interrupted

        result = workflow.invoke(
            Command(
                resume={
                    "perspective_id": "process-first",
                    "human_guidance": None,
                }
            ),
            config=config,
        )

    assert result["post"] == candidate
    assert result["post"].source == "target_url"
    assert result["post"].post_url == TARGET_URL
    assert result["opportunity_evaluation"].classification == "HIGH"
    assert result["research_result"] == make_brief()
    assert result["argument_brief"] == make_argument_brief()
    assert result["perspective_set"] == make_perspective_set()
    assert (
        result["selected_perspective"].perspective.perspective_id
        == "process-first"
    )
    assert result["current_draft"] == "Grounded target draft v1."
    assert result["quality_evaluation"].decision == "PASS"
    assert result["iteration"] == 1
    assert result["status"] == "EVALUATED"
    assert result["next_step"] == "PASS"
    