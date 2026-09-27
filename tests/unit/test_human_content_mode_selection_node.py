import pytest

from app.graph.nodes.human_content_mode_selection_node import (
    human_content_mode_selection_node,
)


def test_human_content_mode_selection_requires_selected_perspective():
    with pytest.raises(
        ValueError,
        match="requires a SelectedPerspective",
    ):
        human_content_mode_selection_node({})


@pytest.mark.parametrize(
    "content_mode",
    [
        "linkedin_post",
        "linkedin_reply",
        "article",
    ],
)
def test_human_content_mode_selection_accepts_valid_modes(
    monkeypatch,
    content_mode,
):
    monkeypatch.setattr(
        "app.graph.nodes.human_content_mode_selection_node.interrupt",
        lambda payload: {"content_mode": content_mode},
    )

    state = {
        "selected_perspective": object(),
    }

    result = human_content_mode_selection_node(state)

    assert result == {
        "content_mode": content_mode,
    }


def test_human_content_mode_selection_rejects_invalid_mode(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.graph.nodes.human_content_mode_selection_node.interrupt",
        lambda payload: {"content_mode": "instagram_reel"},
    )

    state = {
        "selected_perspective": object(),
    }

    with pytest.raises(
        ValueError,
        match="requires a valid content_mode",
    ):
        human_content_mode_selection_node(state)
