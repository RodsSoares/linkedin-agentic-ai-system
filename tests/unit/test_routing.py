import pytest
from app.schemas.opportunity import OpportunityEvaluation
from app.schemas.post import PostCandidate

from app.graph.routing import (
    route_after_evaluation,
    route_after_opportunity_evaluation,
    route_after_scout,
)

def test_route_after_scout_continues_when_post_exists():
    candidate = PostCandidate(
        post_id="post-001",
        author_name="Test Author",
        post_text="AI agents are changing supply chain planning.",
        post_url="https://example.com/post-001",
    )

    state = {
        "post": candidate,
        "status": "CANDIDATE_SELECTED",
    }

    assert (
        route_after_scout(state)
        == "opportunity_evaluation"
    )


def test_route_after_scout_ends_when_no_candidate_found():
    state = {
        "post": None,
        "status": "NO_CANDIDATE_FOUND",
    }

    assert route_after_scout(state) == "end"


def test_route_after_scout_requires_valid_result():
    state = {
        "post": None,
        "status": "RUNNING",
    }

    with pytest.raises(
        ValueError,
        match="Scout routing requires",
    ):
        route_after_scout(state)


def make_opportunity_evaluation(
    classification: str,
) -> OpportunityEvaluation:
    return OpportunityEvaluation(
        topic_relevance=80,
        positioning_fit=80,
        contribution_potential=80,
        engagement_potential=50,
        research_cost=40,
        research_efficiency=60,
        opportunity_score=75.0,
        classification=classification,
    )


def test_route_high_opportunity_to_continue():
    state = {
        "opportunity_evaluation": make_opportunity_evaluation("HIGH"),
    }

    result = route_after_opportunity_evaluation(state)

    assert result == "continue"


def test_route_medium_opportunity_to_queue():
    state = {
        "opportunity_evaluation": make_opportunity_evaluation("MEDIUM"),
    }

    result = route_after_opportunity_evaluation(state)

    assert result == "queue"


def test_route_low_opportunity_to_end():
    state = {
        "opportunity_evaluation": make_opportunity_evaluation("LOW"),
    }

    result = route_after_opportunity_evaluation(state)

    assert result == "end"


def test_route_requires_opportunity_evaluation():
    state = {
        "opportunity_evaluation": None,
    }

    try:
        route_after_opportunity_evaluation(state)
    except ValueError as error:
        assert str(error) == (
            "Routing requires an opportunity evaluation."
        )
    else:
        raise AssertionError(
            "Routing should require an opportunity evaluation."
        )