from app.agents.scout import execute_action
from app.config.settings import SCOUT_READ_CONTEXT_MAX_TOKENS
from app.context_preparation import count_tokens
from app.schemas.scout import ScoutAction, ScoutSelection, ScoutState
from app.schemas.tools import SearchResult


URL = "https://example.com/article"


def fake_search(query: str) -> list[SearchResult]:
    return [
        SearchResult(
            title="Agentic AI article",
            url=URL,
            snippet="Relevant article.",
        )
    ]


def long_reader(url: str) -> str:
    return "agentic supply chain execution " * 4000


def test_scout_bounds_read_content_before_storing_it():
    state = ScoutState(
        objective="Find relevant opportunities."
    )

    execute_action(
        ScoutAction(
            action="SEARCH",
            query="agentic ai supply chain",
            reason="Discover sources.",
        ),
        state,
        search_tool=fake_search,
        read_tool=long_reader,
    )

    execute_action(
        ScoutAction(
            action="READ",
            url=URL,
            reason="Inspect source.",
        ),
        state,
        search_tool=fake_search,
        read_tool=long_reader,
    )

    assert state.last_read_content is not None
    assert (
        count_tokens(state.last_read_content)
        <= SCOUT_READ_CONTEXT_MAX_TOKENS
    )


def test_scout_select_is_idempotent_for_same_url():
    state = ScoutState(
        objective="Find relevant opportunities."
    )

    execute_action(
        ScoutAction(
            action="SEARCH",
            query="agentic ai supply chain",
            reason="Discover sources.",
        ),
        state,
        search_tool=fake_search,
        read_tool=lambda url: "Useful content.",
    )

    execute_action(
        ScoutAction(
            action="READ",
            url=URL,
            reason="Inspect source.",
        ),
        state,
        search_tool=fake_search,
        read_tool=lambda url: "Useful content.",
    )

    selection = ScoutAction(
        action="SELECT",
        reason="Useful opportunity.",
        selection=ScoutSelection(
            reason="Relevant to the objective."
        ),
    )

    execute_action(
        selection,
        state,
        search_tool=fake_search,
        read_tool=lambda url: "Unused.",
    )
    execute_action(
        selection,
        state,
        search_tool=fake_search,
        read_tool=lambda url: "Unused.",
    )
    execute_action(
        selection,
        state,
        search_tool=fake_search,
        read_tool=lambda url: "Unused.",
    )

    assert len(state.candidates) == 1
    assert state.candidates[0].post_url == URL
