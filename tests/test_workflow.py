from unittest.mock import patch

from app.graph.workflow import build_opportunity_workflow
from app.schemas.opportunity import OpportunitySignals
from app.schemas.post import PostCandidate


def make_post() -> PostCandidate:
    return PostCandidate(
        post_id="workflow-test-001",
        post_url="https://linkedin.com/posts/workflow-test-001",
        author_name="Test Author",
        post_text="AI agents can improve supply chain decision-making.",
    )


def test_high_opportunity_routes_to_research():
    signals = OpportunitySignals(
        topic_relevance=95,
        positioning_fit=95,
        contribution_potential=90,
        research_cost=35,
    )

    with patch(
        "app.graph.nodes.opportunity_evaluator_node."
        "evaluate_opportunity_semantics",
        return_value=signals,
    ):
        workflow = build_opportunity_workflow()

        result = workflow.invoke(
            {
                "post": make_post(),
            }
        )

    assert result["opportunity_evaluation"].classification == "HIGH"
    assert result["next_step"] == "research"
    assert result["status"] == "ACCEPTED_FOR_RESEARCH"


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

        result = workflow.invoke(
            {
                "post": make_post(),
            }
        )

    assert result["opportunity_evaluation"].classification == "MEDIUM"
    assert result["next_step"] == "queue"
    assert result["status"] == "QUEUED"


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

        result = workflow.invoke(
            {
                "post": make_post(),
            }
        )

    assert result["opportunity_evaluation"].classification == "LOW"
    assert result.get("next_step") is None