from unittest.mock import patch

import pytest

from app.graph.nodes.research_node import research_node
from app.schemas.opportunity import OpportunityEvaluation
from app.schemas.post import PostCandidate
from app.schemas.research import (
    ResearchBrief,
    ResearchObjective,
    ResearchState,
    ResearchStatus,
)


def make_post() -> PostCandidate:
    return PostCandidate(
        post_id="research-node-001",
        author_name="Test Author",
        post_text="AI agents can support supply chain planning.",
        post_url="https://example.com/research-node-001",
    )


def make_evaluation(
    classification: str = "HIGH",
) -> OpportunityEvaluation:
    return OpportunityEvaluation(
        topic_relevance=90,
        positioning_fit=90,
        contribution_potential=90,
        research_cost=30,
        engagement_potential=50,
        research_efficiency=70,
        opportunity_score=84.5,
        classification=classification,
    )


def make_final_state() -> ResearchState:
    return ResearchState(
        post=make_post(),
        opportunity_evaluation=make_evaluation(),
        research_objective=ResearchObjective(
            question="What evidence supports this opportunity?",
            focus_areas=["agentic planning"],
        ),
        status=ResearchStatus.SUFFICIENT,
    )


def make_brief() -> ResearchBrief:
    return ResearchBrief(
        research_objective=ResearchObjective(
            question="What evidence supports this opportunity?",
            focus_areas=["agentic planning"],
        ),
        summary="Bounded research produced sufficient support.",
        key_findings=["One supported finding."],
        evidence=[],
        counterpoints=[],
        unresolved_questions=[],
        sources=[],
        status=ResearchStatus.SUFFICIENT,
    )


def test_research_node_returns_structured_research_brief():
    final_state = make_final_state()
    brief = make_brief()

    with (
        patch(
            "app.graph.nodes.research_node.run_research_loop",
            return_value=final_state,
        ) as run_mock,
        patch(
            "app.graph.nodes.research_node.build_research_brief",
            return_value=brief,
        ) as brief_mock,
    ):
        result = research_node(
            {
                "post": make_post(),
                "opportunity_evaluation": make_evaluation(),
            }
        )

    assert result["research_result"] == brief
    assert result["status"] == "RESEARCH_COMPLETED"
    assert result["next_step"] == "end"
    run_mock.assert_called_once()
    brief_mock.assert_called_once()


def test_research_node_requires_post():
    with pytest.raises(
        ValueError,
        match="Research workflow requires a PostCandidate",
    ):
        research_node(
            {
                "post": None,
                "opportunity_evaluation": make_evaluation(),
            }
        )


def test_research_node_requires_opportunity_evaluation():
    with pytest.raises(
        ValueError,
        match="Research workflow requires an OpportunityEvaluation",
    ):
        research_node(
            {
                "post": make_post(),
                "opportunity_evaluation": None,
            }
        )


@pytest.mark.parametrize("classification", ["MEDIUM", "LOW"])
def test_research_node_rejects_non_high_opportunities(
    classification: str,
):
    with pytest.raises(
        ValueError,
        match="Research may only execute for HIGH opportunities",
    ):
        research_node(
            {
                "post": make_post(),
                "opportunity_evaluation": make_evaluation(
                    classification=classification,
                ),
            }
        )
