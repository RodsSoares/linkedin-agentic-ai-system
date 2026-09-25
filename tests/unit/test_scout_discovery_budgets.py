from unittest.mock import Mock

import pytest

from app.agents.scout import execute_action
from app.schemas.scout import ScoutAction, ScoutState
from app.schemas.tools import SearchResult
from app.tools.errors import WebToolError


URL_A = "https://example.com/a"
URL_B = "https://example.com/b"


def make_result(url: str) -> SearchResult:
    return SearchResult(
        title="Test result",
        url=url,
        snippet="Relevant test content.",
    )


def test_search_budget_blocks_search_beyond_limit():
    state = ScoutState(
        objective="Find relevant opportunities.",
        max_searches=2,
    )

    search_tool = Mock(return_value=[make_result(URL_A)])

    execute_action(
        action=ScoutAction(
            action="SEARCH",
            query="first query",
            reason="First search.",
        ),
        state=state,
        search_tool=search_tool,
        read_tool=Mock(),
    )

    execute_action(
        action=ScoutAction(
            action="SEARCH",
            query="second query",
            reason="Second search.",
        ),
        state=state,
        search_tool=search_tool,
        read_tool=Mock(),
    )

    with pytest.raises(
        ValueError,
        match="Scout search budget exhausted",
    ):
        execute_action(
            action=ScoutAction(
                action="SEARCH",
                query="third query",
                reason="Should exceed the budget.",
            ),
            state=state,
            search_tool=search_tool,
            read_tool=Mock(),
        )

    assert len(state.search_queries) == 2
    assert search_tool.call_count == 2


def test_read_budget_blocks_read_beyond_limit():
    state = ScoutState(
        objective="Find relevant opportunities.",
        max_reads=1,
        search_results=[
            make_result(URL_A),
            make_result(URL_B),
        ],
    )

    execute_action(
        action=ScoutAction(
            action="READ",
            url=URL_A,
            reason="Inspect first source.",
        ),
        state=state,
        search_tool=Mock(),
        read_tool=Mock(return_value="Useful source content."),
    )

    assert state.read_attempts == 1
    assert state.successful_reads == 1

    with pytest.raises(
        ValueError,
        match="Scout read budget exhausted",
    ):
        execute_action(
            action=ScoutAction(
                action="READ",
                url=URL_B,
                reason="Should exceed the read budget.",
            ),
            state=state,
            search_tool=Mock(),
            read_tool=Mock(return_value="More content."),
        )

    assert state.read_attempts == 1
    assert state.successful_reads == 1


def test_failed_read_is_recorded_and_does_not_block_other_sources():
    state = ScoutState(
        objective="Find relevant opportunities.",
        max_reads=3,
        search_results=[
            make_result(URL_A),
            make_result(URL_B),
        ],
    )

    read_tool = Mock(
        side_effect=[
            WebToolError("HTTP 403"),
            "Useful alternative source content.",
        ]
    )

    with pytest.raises(WebToolError):
        execute_action(
            action=ScoutAction(
                action="READ",
                url=URL_A,
                reason="Inspect first source.",
            ),
            state=state,
            search_tool=Mock(),
            read_tool=read_tool,
        )

    assert state.read_attempts == 1
    assert state.successful_reads == 0
    assert state.blocked_reads == 1
    assert URL_A in state.blocked_urls
    assert URL_A not in state.visited_urls

    execute_action(
        action=ScoutAction(
            action="READ",
            url=URL_B,
            reason="Try an alternative source.",
        ),
        state=state,
        search_tool=Mock(),
        read_tool=read_tool,
    )

    assert state.read_attempts == 2
    assert state.successful_reads == 1
    assert state.blocked_reads == 1
    assert URL_B in state.visited_urls
    assert state.last_read_url == URL_B


def test_blocked_url_cannot_be_retried():
    state = ScoutState(
        objective="Find relevant opportunities.",
        max_reads=3,
        search_results=[make_result(URL_A)],
        blocked_urls=[URL_A],
    )

    read_tool = Mock()

    with pytest.raises(
        ValueError,
        match="Scout attempted to revisit a blocked URL",
    ):
        execute_action(
            action=ScoutAction(
                action="READ",
                url=URL_A,
                reason="Retry blocked source.",
            ),
            state=state,
            search_tool=Mock(),
            read_tool=read_tool,
        )

    assert state.read_attempts == 0
    read_tool.assert_not_called()
