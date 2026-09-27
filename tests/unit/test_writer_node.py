from unittest.mock import patch

import pytest

from app.graph.nodes.writer_node import writer_node
from app.schemas.post import PostCandidate


def make_post() -> PostCandidate:
    return PostCandidate(
        post_id="test-post-001",
        author_name="Test Author",
        post_text="Test source content.",
        post_url="https://example.com/post",
    )

@pytest.mark.parametrize(
    "content_mode",
    [
        "linkedin_reply",
        "linkedin_post",
        "article",
    ],
)
def test_writer_node_passes_content_mode_to_writer(
    content_mode,
):
    state = {
        "post": make_post(),
        "content_mode": content_mode,
        "iteration": 0,
    }

    with patch(
        "app.graph.nodes.writer_node.writer",
        return_value="Generated content.",
    ) as writer_mock:
        result = writer_node(state)

    writer_mock.assert_called_once()

    writer_input = writer_mock.call_args.args[0]

    assert writer_input.content_mode == content_mode

    assert result == {
        "current_draft": "Generated content.",
        "iteration": 1,
        "next_step": "evaluator",
        "status": "DRAFT_READY",
    }


def test_writer_node_defaults_to_linkedin_reply():
    state = {
        "post": make_post(),
        "iteration": 0,
    }

    with patch(
        "app.graph.nodes.writer_node.writer",
        return_value="Generated content.",
    ) as writer_mock:
        writer_node(state)

    writer_input = writer_mock.call_args.args[0]

    assert writer_input.content_mode == "linkedin_reply"


def test_writer_node_preserves_content_mode_during_revision():
    state = {
        "post": make_post(),
        "content_mode": "article",
        "current_draft": "Previous article draft.",
        "iteration": 1,
    }

    with patch(
        "app.graph.nodes.writer_node.writer",
        return_value="Revised article.",
    ) as writer_mock:
        result = writer_node(state)

    writer_input = writer_mock.call_args.args[0]

    assert writer_input.content_mode == "article"
    assert writer_input.previous_draft == "Previous article draft."

    assert result["current_draft"] == "Revised article."
    assert result["iteration"] == 2


def test_writer_node_requires_post():
    state = {
        "post": None,
    }

    with pytest.raises(
        ValueError,
        match="Writer node requires a PostCandidate.",
    ):
        writer_node(state)
