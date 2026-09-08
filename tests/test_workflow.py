from unittest.mock import patch

from app.graph.workflow import build_opportunity_workflow
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


def fake_research_node(state):
    return {
        "research_result": make_research_brief(),
        "next_step": "writer",
        "status": "RESEARCH_COMPLETED",
    }


def fake_writer_node(state):
    return {
        "current_draft": "Grounded draft.",
        "iteration": state.get("iteration", 0) + 1,
        "next_step": "evaluator",
        "status": "DRAFT_READY",
    }


def test_high_opportunity_routes_through_research_to_writer():
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
            "app.graph.workflow.writer_node",
            side_effect=fake_writer_node,
        ),
    ):
        workflow = build_opportunity_workflow()
        result = workflow.invoke({"post": make_post()})

    assert result["opportunity_evaluation"].classification == "HIGH"
    assert result["research_result"] == make_research_brief()
    assert result["current_draft"] == "Grounded draft."
    assert result["next_step"] == "evaluator"
    assert result["status"] == "DRAFT_READY"


def test_medium_opportunity_routes_to_queue():
    signals = OpportunitySignals(
        topic_relevance=70,
        positioning_fit=70,
        contribution_potential=70,
        research_cost=40,
    )

    with patch(
        "app.graph.nodes.opportunity_evaluator_node."
        "evaluate_opportunity_semantics",
        return_value=signals,
    ):
        workflow = build_opportunity_workflow()
        result = workflow.invoke({"post": make_post()})

    assert result["opportunity_evaluation"].classification == "MEDIUM"
    assert result["next_step"] == "queue"
    assert result["status"] == "QUEUED"
    assert result.get("research_result") is None
    assert result.get("current_draft") is None


def test_low_opportunity_ends_workflow():
    signals = OpportunitySignals(
        topic_relevance=60,
        positioning_fit=60,
        contribution_potential=60,
        research_cost=50,
    )

    with patch(
        "app.graph.nodes.opportunity_evaluator_node."
        "evaluate_opportunity_semantics",
        return_value=signals,
    ):
        workflow = build_opportunity_workflow()
        result = workflow.invoke({"post": make_post()})

    assert result["opportunity_evaluation"].classification == "LOW"
    assert result.get("next_step") is None
    assert result.get("research_result") is None
    assert result.get("current_draft") is None
    