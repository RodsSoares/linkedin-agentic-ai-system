from unittest.mock import patch

import pytest

from app.graph.nodes.scout_node import scout_node
from app.schemas.post import PostCandidate
from app.schemas.scout import ScoutState


def build_scout_state(
    candidates: list[PostCandidate],
) -> ScoutState:
    return ScoutState(
        objective="Find relevant AI + Supply Chain opportunities",
        candidates=candidates,
    )


def test_scout_node_sets_selected_candidate_as_post():
    candidate = PostCandidate(
        post_id="post-001",
        author_name="Test Author",
        post_text="AI agents are changing supply chain planning.",
        post_url="https://example.com/post-001",
    )

    scout_state = build_scout_state([candidate])

    with patch(
        "app.graph.nodes.scout_node.run_scout",
        return_value=scout_state,
    ):
        result = scout_node(
            {
                "scout_objective": (
                    "Find relevant AI + Supply Chain opportunities"
                )
            }
        )

    assert result["post"] == candidate
    assert result["status"] == "CANDIDATE_SELECTED"
    assert result["next_step"] == "opportunity_evaluation"


def test_scout_node_ends_when_no_candidate_is_found():
    scout_state = build_scout_state([])

    with patch(
        "app.graph.nodes.scout_node.run_scout",
        return_value=scout_state,
    ):
        result = scout_node(
            {
                "scout_objective": (
                    "Find relevant AI + Supply Chain opportunities"
                )
            }
        )

    assert result["post"] is None
    assert result["status"] == "NO_CANDIDATE_FOUND"
    assert result["next_step"] == "end"


def test_scout_node_rejects_multiple_candidates():
    candidate_1 = PostCandidate(
        post_id="post-001",
        author_name="Author One",
        post_text="First candidate.",
        post_url="https://example.com/post-001",
    )

    candidate_2 = PostCandidate(
        post_id="post-002",
        author_name="Author Two",
        post_text="Second candidate.",
        post_url="https://example.com/post-002",
    )

    scout_state = build_scout_state(
        [candidate_1, candidate_2]
    )

    with patch(
        "app.graph.nodes.scout_node.run_scout",
        return_value=scout_state,
    ):
        with pytest.raises(
            ValueError,
            match="multiple candidates",
        ):
            scout_node(
                {
                    "scout_objective": (
                        "Find relevant AI + Supply Chain opportunities"
                    )
                }
            )


def test_scout_node_requires_objective():
    with pytest.raises(
        ValueError,
        match="scout_objective",
    ):
        scout_node({})