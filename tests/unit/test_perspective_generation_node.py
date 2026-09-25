from unittest.mock import patch

import pytest

from app.graph.nodes.perspective_generation_node import (
    perspective_generation_node,
)


def test_perspective_generation_node_generates_perspective_set():
    argument_brief = object()
    perspective_set = object()

    state = {
        "argument_brief": argument_brief,
    }

    with patch(
        "app.graph.nodes.perspective_generation_node.generate_perspective_set",
        return_value=perspective_set,
    ) as generate_mock:
        result = perspective_generation_node(state)

    generate_mock.assert_called_once_with(argument_brief)

    assert result == {
        "perspective_set": perspective_set,
    }


def test_perspective_generation_node_requires_argument_brief():
    state = {
        "argument_brief": None,
    }

    with pytest.raises(
        ValueError,
        match="Perspective Generation node requires an ArgumentBrief.",
    ):
        perspective_generation_node(state)
