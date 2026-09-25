from unittest.mock import patch

from langgraph.types import Command

from app.graph.workflow import (
    build_opportunity_workflow,
    build_scout_opportunity_workflow,
)
from app.schemas.argument import (
    ArgumentBrief,
    Perspective,
    PerspectiveSet,
)
from app.schemas.opportunity import OpportunitySignals
from app.schemas.post import PostCandidate
from app.schemas.research import (
    ResearchBrief,
    ResearchObjective,
    ResearchStatus,
)
from app.schemas.scout import ScoutState
from app.schemas.evaluator import QualityEvaluation


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


def make_argument_brief() -> ArgumentBrief:
    return ArgumentBrief(
        original_thesis=(
            "AI agents can improve supply chain decision-making."
        ),
        relevant_context=[
            "Operational value depends on how autonomy is designed."
        ],
        strongest_evidence=[],
        strongest_counterevidence=[],
        central_tensions=[
            "Autonomy can improve speed while increasing decision risk."
        ],
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
                    "Shift attention from capability to operational integration."
                ),
            ),
            Perspective(
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
                supporting_evidence=[],
                counterargument=None,
                uncertainty=None,
                contribution=(
                    "Use risk and reversibility to define autonomy boundaries."
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
        "current_draft": f"Grounded draft v{iteration}.",
        "iteration": iteration,
        "next_step": "evaluator",
        "status": "DRAFT_READY",
    }


def evaluation(
    decision: str,
    revision_instruction: str | None = None,
) -> QualityEvaluation:
    return QualityEvaluation(
        factual_accuracy=100,
        relevance=100,
        voice_match=100,
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
            "quality_evaluation": evaluation(
                decision,
                instruction,
            ),
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


def invoke_until_human_selection(
    workflow,
    initial_state,
    thread_id: str,
):
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    interrupted = workflow.invoke(
        initial_state,
        config=config,
    )

    assert "__interrupt__" in interrupted

    interrupt_payload = interrupted["__interrupt__"][0].value

    assert interrupt_payload["type"] == "perspective_selection"
    assert [
        perspective["perspective_id"]
        for perspective in interrupt_payload["perspectives"]
    ] == [
        "operating-model",
        "risk-calibrated-autonomy",
    ]

    return config


def resume_with_selected_perspective(
    workflow,
    config,
):
    return workflow.invoke(
        Command(
            resume={
                "perspective_id": "risk-calibrated-autonomy",
                "human_guidance": (
                    "Connect this with practical operational decision making."
                ),
            }
        ),
        config=config,
    )


def workflow_patches(evaluator_decisions):
    return (
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
            side_effect=evaluator_with(evaluator_decisions),
        ),
    )


def test_high_opportunity_executes_human_centered_flow_and_passes():
    patches = workflow_patches(["PASS"])

    with (
        patches[0],
        patches[1],
        patches[2],
        patches[3],
        patches[4],
        patches[5],
    ):
        workflow = build_opportunity_workflow()

        config = invoke_until_human_selection(
            workflow,
            {"post": make_post()},
            "high-opportunity-pass",
        )

        result = resume_with_selected_perspective(
            workflow,
            config,
        )

    assert result["opportunity_evaluation"].classification == "HIGH"
    assert result["research_result"] == make_brief()
    assert result["argument_brief"] == make_argument_brief()
    assert result["perspective_set"] == make_perspective_set()
    assert (
        result["selected_perspective"].perspective.perspective_id
        == "risk-calibrated-autonomy"
    )
    assert result["current_draft"] == "Grounded draft v1."
    assert result["quality_evaluation"].decision == "PASS"
    assert result["iteration"] == 1
    assert result["status"] == "EVALUATED"
    assert result["next_step"] == "PASS"


def test_high_opportunity_revise_returns_only_to_writer_then_passes():
    research_calls = 0
    argument_calls = 0
    perspective_calls = 0

    def counted_research_node(state):
        nonlocal research_calls
        research_calls += 1
        return fake_research_node(state)

    def counted_argument_node(state):
        nonlocal argument_calls
        argument_calls += 1
        return fake_argument_intelligence_node(state)

    def counted_perspective_node(state):
        nonlocal perspective_calls
        perspective_calls += 1
        return fake_perspective_generation_node(state)

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
            "app.graph.workflow.argument_intelligence_node",
            side_effect=counted_argument_node,
        ),
        patch(
            "app.graph.workflow.perspective_generation_node",
            side_effect=counted_perspective_node,
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

        config = invoke_until_human_selection(
            workflow,
            {"post": make_post()},
            "high-opportunity-revise",
        )

        result = resume_with_selected_perspective(
            workflow,
            config,
        )

    assert research_calls == 1
    assert argument_calls == 1
    assert perspective_calls == 1
    assert result["current_draft"] == "Grounded draft v2."
    assert result["quality_evaluation"].decision == "PASS"
    assert result["iteration"] == 2


def test_high_opportunity_reject_ends_without_revision():
    patches = workflow_patches(["REJECT"])

    with (
        patches[0],
        patches[1],
        patches[2],
        patches[3],
        patches[4],
        patches[5],
    ):
        workflow = build_opportunity_workflow()

        config = invoke_until_human_selection(
            workflow,
            {"post": make_post()},
            "high-opportunity-reject",
        )

        result = resume_with_selected_perspective(
            workflow,
            config,
        )

    assert result["quality_evaluation"].decision == "REJECT"
    assert result["iteration"] == 1
    assert result["status"] == "EVALUATED"
    assert result["next_step"] == "REJECT"


def test_high_opportunity_revision_loop_stops_at_existing_iteration_limit():
    research_calls = 0
    argument_calls = 0
    perspective_calls = 0

    def counted_research_node(state):
        nonlocal research_calls
        research_calls += 1
        return fake_research_node(state)

    def counted_argument_node(state):
        nonlocal argument_calls
        argument_calls += 1
        return fake_argument_intelligence_node(state)

    def counted_perspective_node(state):
        nonlocal perspective_calls
        perspective_calls += 1
        return fake_perspective_generation_node(state)

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
            "app.graph.workflow.argument_intelligence_node",
            side_effect=counted_argument_node,
        ),
        patch(
            "app.graph.workflow.perspective_generation_node",
            side_effect=counted_perspective_node,
        ),
        patch(
            "app.graph.workflow.writer_node",
            side_effect=fake_writer_node,
        ),
        patch(
            "app.graph.workflow.evaluator_node",
            side_effect=evaluator_with(
                ["REVISE", "REVISE", "REVISE"]
            ),
        ),
    ):
        workflow = build_opportunity_workflow()

        config = invoke_until_human_selection(
            workflow,
            {"post": make_post()},
            "high-opportunity-limit",
        )

        result = resume_with_selected_perspective(
            workflow,
            config,
        )

    assert research_calls == 1
    assert argument_calls == 1
    assert perspective_calls == 1
    assert result["iteration"] == 3
    assert result["quality_evaluation"].decision == "REVISE"
    assert result["status"] == "EVALUATED"
    assert result["next_step"] == "REVISE"


def test_scout_high_opportunity_executes_full_human_centered_path():
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
            side_effect=evaluator_with(["PASS"]),
        ),
    ):
        workflow = build_scout_opportunity_workflow()

        config = invoke_until_human_selection(
            workflow,
            {
                "scout_objective": (
                    "Find AI + Supply Chain opportunities"
                ),
            },
            "scout-high-opportunity-pass",
        )

        result = resume_with_selected_perspective(
            workflow,
            config,
        )

    assert result["post"] == make_post()
    assert result["opportunity_evaluation"].classification == "HIGH"
    assert result["research_result"] == make_brief()
    assert result["argument_brief"] == make_argument_brief()
    assert result["perspective_set"] == make_perspective_set()
    assert (
        result["selected_perspective"].perspective.perspective_id
        == "risk-calibrated-autonomy"
    )
    assert result["current_draft"] == "Grounded draft v1."
    assert result["quality_evaluation"].decision == "PASS"
    assert result["iteration"] == 1
    assert result["status"] == "EVALUATED"
    assert result["next_step"] == "PASS"
    