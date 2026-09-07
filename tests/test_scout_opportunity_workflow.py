from unittest.mock import patch

from app.graph.workflow import build_scout_opportunity_workflow
from app.schemas.opportunity import OpportunitySignals
from app.schemas.post import PostCandidate
from app.schemas.scout import ScoutState


def make_candidate() -> PostCandidate:
    return PostCandidate(
        post_id="scout-workflow-001",
        author_name="Test Author",
        post_text=(
            "AI agents can improve supply chain decision-making."
        ),
        post_url="https://example.com/scout-workflow-001",
    )


def make_scout_state(
    candidates: list[PostCandidate],
) -> ScoutState:
    return ScoutState(
        objective="Find AI + Supply Chain opportunities",
        candidates=candidates,
    )


def test_scout_candidate_high_opportunity_routes_to_research():
    scout_state = make_scout_state(
        [make_candidate()]
    )

    signals = OpportunitySignals(
        topic_relevance=95,
        positioning_fit=95,
        contribution_potential=90,
        research_cost=35,
    )

    with (
        patch(
            "app.graph.nodes.scout_node.run_scout",
            return_value=scout_state,
        ),
        patch(
            "app.graph.nodes.opportunity_evaluator_node."
            "evaluate_opportunity_semantics",
            return_value=signals,
        ),
    ):
        workflow = build_scout_opportunity_workflow()

        result = workflow.invoke(
            {
                "scout_objective": (
                    "Find AI + Supply Chain opportunities"
                ),
            }
        )

    assert result["post"] == make_candidate()
    assert (
        result["opportunity_evaluation"].classification
        == "HIGH"
    )
    assert result["next_step"] == "research"
    assert result["status"] == "ACCEPTED_FOR_RESEARCH"


def test_scout_without_candidate_ends_before_evaluation():
    scout_state = make_scout_state([])

    with (
        patch(
            "app.graph.nodes.scout_node.run_scout",
            return_value=scout_state,
        ),
        patch(
            "app.graph.nodes.opportunity_evaluator_node."
            "evaluate_opportunity_semantics"
        ) as evaluator_mock,
    ):
        workflow = build_scout_opportunity_workflow()

        result = workflow.invoke(
            {
                "scout_objective": (
                    "Find AI + Supply Chain opportunities"
                ),
            }
        )

    assert result["post"] is None
    assert result["status"] == "NO_CANDIDATE_FOUND"
    assert result["next_step"] == "end"

    evaluator_mock.assert_not_called()