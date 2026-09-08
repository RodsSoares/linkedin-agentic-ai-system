from unittest.mock import patch

from app.graph.workflow import (
    build_opportunity_workflow,
    build_scout_opportunity_workflow,
)
from app.schemas.opportunity import OpportunitySignals
from app.schemas.post import PostCandidate
from app.schemas.research import (
    ResearchBrief,
    ResearchObjective,
    ResearchStatus,
)
from app.schemas.scout import ScoutState


def make_post() -> PostCandidate:
    return PostCandidate(
        post_id="research-workflow-001",
        author_name="Test Author",
        post_text="AI agents can improve supply chain decision-making.",
        post_url="https://example.com/research-workflow-001",
    )


def make_brief() -> ResearchBrief:
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
        "research_result": make_brief(),
        "status": "RESEARCH_COMPLETED",
        "next_step": "writer",
    }


def fake_writer_node(state):
    return {
        "current_draft": "Grounded draft.",
        "iteration": state.get("iteration", 0) + 1,
        "next_step": "evaluator",
        "status": "DRAFT_READY",
    }


def high_signals() -> OpportunitySignals:
    return OpportunitySignals(
        topic_relevance=95,
        positioning_fit=95,
        contribution_potential=90,
        research_cost=35,
    )


def test_high_opportunity_executes_research_and_writer():
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
    ):
        workflow = build_opportunity_workflow()
        result = workflow.invoke({"post": make_post()})

    assert result["opportunity_evaluation"].classification == "HIGH"
    assert result["research_result"] == make_brief()
    assert result["current_draft"] == "Grounded draft."
    assert result["status"] == "DRAFT_READY"
    assert result["next_step"] == "evaluator"


def test_scout_high_opportunity_executes_research_and_writer():
    scout_state = ScoutState(
        objective="Find AI + Supply Chain opportunities",
        candidates=[make_post()],
    )

    with (
        patch(
            "app.graph.nodes.scout_node.run_scout",
            return_value=scout_state,
        ),
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
    ):
        workflow = build_scout_opportunity_workflow()
        result = workflow.invoke(
            {
                "scout_objective": "Find AI + Supply Chain opportunities",
            }
        )

    assert result["post"] == make_post()
    assert result["opportunity_evaluation"].classification == "HIGH"
    assert result["research_result"] == make_brief()
    assert result["current_draft"] == "Grounded draft."
    assert result["status"] == "DRAFT_READY"
    assert result["next_step"] == "evaluator"
    