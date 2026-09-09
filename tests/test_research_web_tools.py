from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.graph.nodes.research_node import research_node


def test_research_node_uses_selected_web_tools():
    fake_search_tool = Mock(name="fake_search_tool")
    fake_read_tool = Mock(name="fake_read_tool")
    fake_research_state = Mock(name="research_state")
    fake_final_state = Mock(name="final_state")
    fake_brief = Mock(name="research_brief")

    state = {
        "post": Mock(name="post"),
        "opportunity_evaluation": SimpleNamespace(
            classification="HIGH"
        ),
    }

    with (
        patch(
            "app.graph.nodes.research_node.get_web_tools",
            return_value=(fake_search_tool, fake_read_tool),
        ) as mocked_get_web_tools,
        patch(
            "app.graph.nodes.research_node.ResearchState",
            return_value=fake_research_state,
        ),
        patch(
            "app.graph.nodes.research_node.run_research_loop",
            return_value=fake_final_state,
        ) as mocked_run_loop,
        patch(
            "app.graph.nodes.research_node.build_research_brief",
            return_value=fake_brief,
        ),
    ):
        result = research_node(state)

    mocked_get_web_tools.assert_called_once_with()

    call_kwargs = mocked_run_loop.call_args.kwargs
    assert call_kwargs["search_tool"] is fake_search_tool
    assert call_kwargs["read_tool"] is fake_read_tool

    assert result == {
        "research_result": fake_brief,
        "next_step": "end",
        "status": "RESEARCH_COMPLETED",
    }


def test_research_node_does_not_call_web_tool_selector_for_non_high():
    state = {
        "post": Mock(name="post"),
        "opportunity_evaluation": SimpleNamespace(
            classification="MEDIUM"
        ),
    }

    with patch(
        "app.graph.nodes.research_node.get_web_tools"
    ) as mocked_get_web_tools:
        try:
            research_node(state)
        except ValueError as error:
            assert str(error) == (
                "Research may only execute for HIGH opportunities."
            )
        else:
            raise AssertionError(
                "Research should reject non-HIGH opportunities."
            )

    mocked_get_web_tools.assert_not_called()
