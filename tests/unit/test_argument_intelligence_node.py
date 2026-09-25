from unittest.mock import patch

import pytest

from app.graph.nodes.argument_intelligence_node import (
    argument_intelligence_node,
)


def test_argument_intelligence_node_generates_argument_brief():
    research_brief = object()
    argument_brief = object()

    state = {
        "research_result": research_brief,
    }

    with patch(
        "app.graph.nodes.argument_intelligence_node.generate_argument_brief",
        return_value=argument_brief,
    ) as generate_mock:
        result = argument_intelligence_node(state)

    generate_mock.assert_called_once_with(research_brief)

    assert result == {
        "argument_brief": argument_brief,
    }


def test_argument_intelligence_node_requires_research_brief():
    state = {
        "research_result": None,
    }

    with pytest.raises(
        ValueError,
        match="Argument Intelligence node requires a ResearchBrief.",
    ):
        argument_intelligence_node(state)
