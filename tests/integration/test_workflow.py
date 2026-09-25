from unittest.mock import patch

from langgraph.types import Command

from app.graph.workflow import build_opportunity_workflow
from app.schemas.argument import (
    ArgumentBrief,
    Perspective,
    PerspectiveSet,
)
from app.schemas.evaluator import QualityEvaluation
from app.schemas.opportunity import OpportunitySignals
from app.schemas.post import PostCandidate
from app.schemas.research import (
    ResearchBrief,
    ResearchObjective,
    ResearchStatus,
)


def make_post() -> PostCandidate:
    return PostCandidate(
        post_id="workflow-test-001",
        post_url="https://linkedin.com/posts/workflow-test-001",
        author_name="Test Author",
        post_text="AI agents can improve supply chain decision-making.",
    )


def make_research_brief() -> ResearchBrief:
    return ResearchBrief(
        research_objective=ResearchObjective(
            question="What evidence supports this opportunity?",
            focus_areas=["agentic planning"],
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
            "AI agents can improve supply chain decision-making."
        ),
        relevant_context=[],
        strongest_evidence=[],
        strongest_counterevidence=[],
        central_tensions=[],
        uncertainties=[],
        contribution_areas=[
            "Operating-model design",
            "Risk-calibrated autonomy",
        ],
    )


def make_perspective_set() -> PerspectiveSet:
    return PerspectiveSet(
        perspectives=[
            Perspective(
                perspective_id="operating-model",
                label="Operating model",
                core_argument=(
                    "AI-agent value depends on operating-model design."
                ),
                why_it_matters=(
                    "Technical capability alone does not guarantee "
                    "operational value."
                ),
                supporting_evidence=[],
                counterargument=None,
                uncertainty=None,
                contribution=(
                    "Focus on operational integration."
                ),
            ),
            Perspective(
                perspective_id="risk-calibrated-autonomy",
                label="Risk-calibrated autonomy",
                core_argument=(
                    "Autonomy should depend on decision risk."
                ),
                why_it_matters=(
                    "Different decisions justify different levels "
                    "of human control."
                ),
                supporting_evidence=[],
                counterargument=None,
                uncertainty=None,
                contribution=(
                    "Define autonomy boundaries using risk."
                ),
            ),
        ]
    )


def fake_research_node(state):
    return {
        "research_result": make_research_brief(),
        "next_step": "argument_intelligence",
        "status": "RESEARCH_COMPLETED",
    }


def fake_argument_intelligence_node(state):
    return {
        "argument_brief": make_argument_brief(),
    }


def fake_perspective_generation_node(state):
    return {
        "perspective_set": make_perspective_set(),
    }


def fake_writer_node(state):
    assert state["selected_perspective"] is not None

    return {
        "current_draft": "Grounded draft.",
        "iteration": state.get("iteration", 0) + 1,
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


def test_high_opportunity_routes_through_human_centered_flow():
    signals = OpportunitySignals(
        topic_relevance=95,
        positioning_fit=95,
        contribution_potential=90,
        research_cost=35,
    )

    with (
        patch(
            "app.graph.nodes.opportunity_evaluator_node."
            "evaluate_opportunity_semantics",
            return_value=signals,
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
                "thread_id": "workflow-high-opportunity",
            }
        }

        interrupted = workflow.invoke(
            {"post": make_post()},
            config=config,
        )

        assert "__interrupt__" in interrupted

        result = workflow.invoke(
            Command(
                resume={
                    "perspective_id": "risk-calibrated-autonomy",
                    "human_guidance": None,
                }
            ),
            config=config,
        )

    assert result["opportunity_evaluation"].classification == "HIGH"
    assert result["research_result"] == make_research_brief()
    assert result["argument_brief"] == make_argument_brief()
    assert result["perspective_set"] == make_perspective_set()
    assert (
        result["selected_perspective"].perspective.perspective_id
        == "risk-calibrated-autonomy"
    )
    assert result["current_draft"] == "Grounded draft."
    assert result["quality_evaluation"].decision == "PASS"
    assert result["next_step"] == "PASS"
    assert result["status"] == "EVALUATED"


def test_medium_opportunity_routes_to_queue():
    signals = OpportunitySignals(
        topic_relevance=70,
        positioning_fit=70,
        contribution_potential=70,
        research_cost=40,
    )

    with (
        patch(
            "app.graph.nodes.opportunity_evaluator_node."
            "evaluate_opportunity_semantics",
            return_value=signals,
        ),
        patch(
            "app.graph.workflow.evaluator_node"
        ) as quality_evaluator_mock,
    ):
        workflow = build_opportunity_workflow()

        result = workflow.invoke(
            {"post": make_post()},
            config={
                "configurable": {
                    "thread_id": "workflow-medium-opportunity",
                }
            },
        )

    assert result["opportunity_evaluation"].classification == "MEDIUM"
    assert result["next_step"] == "queue"
    assert result["status"] == "QUEUED"
    assert result.get("research_result") is None
    assert result.get("argument_brief") is None
    assert result.get("perspective_set") is None
    assert result.get("selected_perspective") is None
    assert result.get("current_draft") is None
    quality_evaluator_mock.assert_not_called()


def test_low_opportunity_ends_workflow():
    signals = OpportunitySignals(
        topic_relevance=60,
        positioning_fit=60,
        contribution_potential=60,
        research_cost=50,
    )

    with (
        patch(
            "app.graph.nodes.opportunity_evaluator_node."
            "evaluate_opportunity_semantics",
            return_value=signals,
        ),
        patch(
            "app.graph.workflow.evaluator_node"
        ) as quality_evaluator_mock,
    ):
        workflow = build_opportunity_workflow()

        result = workflow.invoke(
            {"post": make_post()},
            config={
                "configurable": {
                    "thread_id": "workflow-low-opportunity",
                }
            },
        )

    assert result["opportunity_evaluation"].classification == "LOW"
    assert result.get("next_step") is None
    assert result.get("research_result") is None
    assert result.get("argument_brief") is None
    assert result.get("perspective_set") is None
    assert result.get("selected_perspective") is None
    assert result.get("current_draft") is None
    quality_evaluator_mock.assert_not_called()
