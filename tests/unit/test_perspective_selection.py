import pytest

from app.components.perspective_selection import select_perspective
from app.schemas.argument import (
    Perspective,
    PerspectiveSet,
)


def _make_perspective_set() -> PerspectiveSet:
    perspective_a = Perspective(
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
    )

    perspective_b = Perspective(
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
    )

    return PerspectiveSet(
        perspectives=[
            perspective_a,
            perspective_b,
        ]
    )


def test_select_perspective_resolves_human_selected_id():
    perspective_set = _make_perspective_set()

    result = select_perspective(
        perspective_set=perspective_set,
        perspective_id="risk-calibrated-autonomy",
    )

    assert (
        result.perspective.perspective_id
        == "risk-calibrated-autonomy"
    )


def test_select_perspective_preserves_original_perspective_object():
    perspective_set = _make_perspective_set()

    result = select_perspective(
        perspective_set=perspective_set,
        perspective_id="operating-model",
    )

    assert result.perspective is perspective_set.perspectives[0]


def test_select_perspective_preserves_human_guidance():
    perspective_set = _make_perspective_set()

    result = select_perspective(
        perspective_set=perspective_set,
        perspective_id="risk-calibrated-autonomy",
        human_guidance=(
            "Connect this with practical operational decision making."
        ),
    )

    assert result.human_guidance == (
        "Connect this with practical operational decision making."
    )


def test_select_perspective_strips_human_guidance():
    perspective_set = _make_perspective_set()

    result = select_perspective(
        perspective_set=perspective_set,
        perspective_id="operating-model",
        human_guidance="  Keep the argument practical.  ",
    )

    assert result.human_guidance == "Keep the argument practical."


def test_select_perspective_converts_blank_guidance_to_none():
    perspective_set = _make_perspective_set()

    result = select_perspective(
        perspective_set=perspective_set,
        perspective_id="operating-model",
        human_guidance="   ",
    )

    assert result.human_guidance is None


def test_select_perspective_rejects_unknown_id():
    perspective_set = _make_perspective_set()

    with pytest.raises(
        ValueError,
        match="Perspective not found",
    ):
        select_perspective(
            perspective_set=perspective_set,
            perspective_id="does-not-exist",
        )


def test_select_perspective_rejects_empty_id():
    perspective_set = _make_perspective_set()

    with pytest.raises(
        ValueError,
        match="perspective_id must not be empty",
    ):
        select_perspective(
            perspective_set=perspective_set,
            perspective_id="   ",
        )


def test_select_perspective_strips_selected_id():
    perspective_set = _make_perspective_set()

    result = select_perspective(
        perspective_set=perspective_set,
        perspective_id="  operating-model  ",
    )

    assert result.perspective is perspective_set.perspectives[0]