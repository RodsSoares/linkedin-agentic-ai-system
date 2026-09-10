from types import SimpleNamespace
from unittest.mock import patch

from app.agents.scout import run_scout
from app.agents.research import _execute_read, _execute_search
from app.schemas.scout import ScoutAction
from app.schemas.tools import SearchResult
from app.tools.errors import WebToolError


def test_scout_recovers_after_web_reader_failure():
    blocked_url = "https://blocked.example/article"
    observed_errors: list[str | None] = []

    actions = [
        ScoutAction(
            action="SEARCH",
            query="agentic ai supply chain",
            reason="Discover relevant sources.",
        ),
        ScoutAction(
            action="READ",
            url=blocked_url,
            reason="Inspect the most relevant source.",
        ),
        ScoutAction(
            action="FINISH",
            reason="Stop after receiving tool feedback.",
        ),
    ]

    def decide(state):
        observed_errors.append(state.last_error)
        return actions[len(observed_errors) - 1]

    def search_tool(query: str) -> list[SearchResult]:
        return [
            SearchResult(
                title="Blocked source",
                url=blocked_url,
                snippet="Relevant result.",
            )
        ]

    def read_tool(url: str) -> str:
        raise WebToolError("Web reader returned HTTP 403.")

    with patch(
        "app.agents.scout.decide_next_action",
        side_effect=decide,
    ):
        state = run_scout(
            objective="Find relevant opportunities.",
            search_tool=search_tool,
            read_tool=read_tool,
            max_steps=5,
        )

    assert observed_errors[2] == (
        "Web tool failure: Web reader returned HTTP 403."
    )
    assert blocked_url not in state.visited_urls
    assert state.last_read_url is None
    assert state.last_read_content is None
    assert state.status == "FINISHED"
    assert state.steps == 3


def test_scout_recovers_after_web_search_failure():
    observed_errors: list[str | None] = []

    actions = [
        ScoutAction(
            action="SEARCH",
            query="agentic ai supply chain",
            reason="Discover relevant sources.",
        ),
        ScoutAction(
            action="FINISH",
            reason="Stop after receiving search failure feedback.",
        ),
    ]

    def decide(state):
        observed_errors.append(state.last_error)
        return actions[len(observed_errors) - 1]

    def search_tool(query: str) -> list[SearchResult]:
        raise WebToolError("Brave Search returned HTTP 429.")

    with patch(
        "app.agents.scout.decide_next_action",
        side_effect=decide,
    ):
        state = run_scout(
            objective="Find relevant opportunities.",
            search_tool=search_tool,
            read_tool=lambda url: "unused",
            max_steps=5,
        )

    assert observed_errors[1] == (
        "Web tool failure: Brave Search returned HTTP 429."
    )
    assert state.search_queries == ["agentic ai supply chain"]
    assert state.status == "FINISHED"
    assert state.steps == 2


def test_research_search_failure_is_recoverable_and_consumes_budget():
    state = SimpleNamespace(
        search_queries=[],
        search_results=[],
        search_count=0,
        steps=0,
        last_error=None,
    )

    action = SimpleNamespace(
        search_query="agentic ai supply chain",
    )

    def search_tool(query: str) -> list[SearchResult]:
        raise WebToolError("Brave Search request timed out.")

    result = _execute_search(
        state=state,
        action=action,
        search_tool=search_tool,
    )

    assert result is state
    assert state.search_queries == ["agentic ai supply chain"]
    assert state.search_count == 1
    assert state.steps == 1
    assert state.search_results == []
    assert state.last_error == (
        "Web search failed: Brave Search request timed out."
    )


def test_research_read_failure_allows_next_source_to_succeed():
    blocked_url = "https://blocked.example/article"
    readable_url = "https://readable.example/article"

    state = SimpleNamespace(
        search_results=[
            SearchResult(
                title="Blocked source",
                url=blocked_url,
                snippet="Relevant but blocked.",
            ),
            SearchResult(
                title="Readable source",
                url=readable_url,
                snippet="Relevant and readable.",
            ),
        ],
        visited_urls=[],
        read_sources=[],
        read_count=0,
        steps=0,
        last_error=None,
    )

    def read_tool(url: str) -> str:
        if url == blocked_url:
            raise WebToolError("Web reader returned HTTP 403.")

        return "Useful evidence from the readable source."

    blocked_action = SimpleNamespace(
        url=blocked_url,
    )

    _execute_read(
        state=state,
        action=blocked_action,
        read_tool=read_tool,
    )

    assert blocked_url in state.visited_urls
    assert state.read_count == 1
    assert state.steps == 1
    assert state.read_sources == []
    assert state.last_error == (
        "Web read failed for "
        f"{blocked_url}: Web reader returned HTTP 403."
    )

    readable_action = SimpleNamespace(
        url=readable_url,
    )

    _execute_read(
        state=state,
        action=readable_action,
        read_tool=read_tool,
    )

    assert readable_url in state.visited_urls
    assert state.read_count == 2
    assert state.steps == 2
    assert len(state.read_sources) == 1
    assert state.read_sources[0].url == readable_url
    assert state.read_sources[0].content == (
        "Useful evidence from the readable source."
    )
    assert state.last_error is None
    