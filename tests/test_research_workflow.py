from types import SimpleNamespace
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
    iteration = state.get("iteration", 0) + 1
    return {
        "current_draft": f"Grounded draft v{iteration}.",
        "iteration": iteration,
        "next_step": "evaluator",
        "status": "DRAFT_READY",
    }


def evaluation(decision: str, revision_instruction: str | None = None):
    return SimpleNamespace(
        decision=decision,
        revision_instruction=revision_instruction,
    )


def evaluator_with(decisions: list[str]):
    remaining = iter(decisions)

    def fake_evaluator_node(state):
        decision = next(remaining)
        instruction = (
            "Make the contribution more specific."
            if decision == "REVISE"
            else None
        )
        return {
            "quality_evaluation": evaluation(decision, instruction),
            "next_step": decision,
            "status": "EVALUATED",
        }

    return fake_evaluator_node


def high_signals() -> OpportunitySignals:
    return OpportunitySignals(
        topic_relevance=95,
        positioning_fit=95,
        contribution_potential=90,
        research_cost=35,
    )


def test_high_opportunity_executes_research_writer_and_evaluator_pass():
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
            side_effect=evaluator_with(["PASS"]),
        ),
    ):
        workflow = build_opportunity_workflow()
        result = workflow.invoke({"post": make_post()})

    assert result["opportunity_evaluation"].classification == "HIGH"
    assert result["research_result"] == make_brief()
    assert result["current_draft"] == "Grounded draft v1."
    assert result["quality_evaluation"].decision == "PASS"
    assert result["iteration"] == 1
    assert result["status"] == "EVALUATED"
    assert result["next_step"] == "PASS"


def test_high_opportunity_revise_returns_only_to_writer_then_passes():
    research_calls = 0

    def counted_research_node(state):
        nonlocal research_calls
        research_calls += 1
        return fake_research_node(state)

    with (
        patch(
            "app.graph.nodes.opportunity_evaluator_node."
            "evaluate_opportunity_semantics",
            return_value=high_signals(),
        ),
        patch(
            "app.graph.workflow.research_node",
            side_effect=counted_research_node,
        ),
        patch(
            "app.graph.workflow.writer_node",
            side_effect=fake_writer_node,
        ),
        patch(
            "app.graph.workflow.evaluator_node",
            side_effect=evaluator_with(["REVISE", "PASS"]),
        ),
    ):
        workflow = build_opportunity_workflow()
        result = workflow.invoke({"post": make_post()})

    assert research_calls == 1
    assert result["research_result"] == make_brief()
    assert result["current_draft"] == "Grounded draft v2."
    assert result["quality_evaluation"].decision == "PASS"
    assert result["iteration"] == 2


def test_high_opportunity_reject_ends_without_revision():
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
            side_effect=evaluator_with(["REJECT"]),
        ),
    ):
        workflow = build_opportunity_workflow()
        result = workflow.invoke({"post": make_post()})

    assert result["quality_evaluation"].decision == "REJECT"
    assert result["iteration"] == 1
    assert result["status"] == "EVALUATED"
    assert result["next_step"] == "REJECT"


def test_high_opportunity_revision_loop_stops_at_existing_iteration_limit():
    research_calls = 0

    def counted_research_node(state):
        nonlocal research_calls
        research_calls += 1
        return fake_research_node(state)

    with (
        patch(
            "app.graph.nodes.opportunity_evaluator_node."
            "evaluate_opportunity_semantics",
            return_value=high_signals(),
        ),
        patch(
            "app.graph.workflow.research_node",
            side_effect=counted_research_node,
        ),
        patch(
            "app.graph.workflow.writer_node",
            side_effect=fake_writer_node,
        ),
        patch(
            "app.graph.workflow.evaluator_node",
            side_effect=evaluator_with(["REVISE", "REVISE", "REVISE"]),
        ),
    ):
        workflow = build_opportunity_workflow()
        result = workflow.invoke({"post": make_post()})

    assert research_calls == 1
    assert result["iteration"] == 3
    assert result["quality_evaluation"].decision == "REVISE"
    assert result["status"] == "EVALUATED"
    assert result["next_step"] == "REVISE"


def test_scout_high_opportunity_executes_full_path_to_evaluator():
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
        patch(
            "app.graph.workflow.evaluator_node",
            side_effect=evaluator_with(["PASS"]),
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
    assert result["current_draft"] == "Grounded draft v1."
    assert result["quality_evaluation"].decision == "PASS"
    assert result["iteration"] == 1
    assert result["status"] == "EVALUATED"
    assert result["next_step"] == "PASS"
