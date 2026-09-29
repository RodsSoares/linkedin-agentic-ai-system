import pytest

from app.graph.nodes.human_final_refinement_node import (
    human_final_refinement_node,
)


class _PassingEvaluation:
    decision = "PASS"


class _FailingEvaluation:
    decision = "REVISE"


def _valid_state() -> dict:
    return {
        "current_draft": "A valid final draft.",
        "quality_evaluation": _PassingEvaluation(),
    }


def test_human_final_refinement_requires_current_draft():
    state = {
        "current_draft": None,
        "quality_evaluation": _PassingEvaluation(),
    }

    with pytest.raises(
        ValueError,
        match="requires a current draft",
    ):
        human_final_refinement_node(state)


def test_human_final_refinement_requires_quality_evaluation():
    state = {
        "current_draft": "A valid final draft.",
        "quality_evaluation": None,
    }

    with pytest.raises(
        ValueError,
        match="requires a quality evaluation",
    ):
        human_final_refinement_node(state)


def test_human_final_refinement_requires_pass_evaluation():
    state = {
        "current_draft": "A valid final draft.",
        "quality_evaluation": _FailingEvaluation(),
    }

    with pytest.raises(
        ValueError,
        match="requires a PASS quality evaluation",
    ):
        human_final_refinement_node(state)


def test_human_final_refinement_accepts_draft(monkeypatch):
    monkeypatch.setattr(
        "app.graph.nodes.human_final_refinement_node.interrupt",
        lambda payload: {"action": "accept"},
    )

    result = human_final_refinement_node(_valid_state())

    assert result == {
        "final_refinement_action": "accept",
        "final_refinement_guidance": None,
    }


def test_human_final_refinement_accepts_refinement_guidance(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.graph.nodes.human_final_refinement_node.interrupt",
        lambda payload: {
            "action": "refine",
            "guidance": "Make the opening more direct.",
        },
    )

    result = human_final_refinement_node(_valid_state())

    assert result == {
        "final_refinement_action": "refine",
        "final_refinement_guidance": "Make the opening more direct.",
    }


@pytest.mark.parametrize(
    "decision",
    [
        None,
        "invalid",
        {},
    ],
)
def test_human_final_refinement_rejects_invalid_action(
    monkeypatch,
    decision,
):
    monkeypatch.setattr(
        "app.graph.nodes.human_final_refinement_node.interrupt",
        lambda payload: decision,
    )

    with pytest.raises(ValueError):
        human_final_refinement_node(_valid_state())


@pytest.mark.parametrize(
    "guidance",
    [
        None,
        "",
        "   ",
        123,
    ],
)
def test_human_final_refinement_requires_guidance_for_refine(
    monkeypatch,
    guidance,
):
    monkeypatch.setattr(
        "app.graph.nodes.human_final_refinement_node.interrupt",
        lambda payload: {
            "action": "refine",
            "guidance": guidance,
        },
    )

    with pytest.raises(
        ValueError,
        match="guidance must be a non-empty string",
    ):
        human_final_refinement_node(_valid_state())
