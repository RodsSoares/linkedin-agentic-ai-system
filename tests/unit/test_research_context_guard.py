from types import SimpleNamespace

from app.agents.research import _execute_read
from app.config.settings import RESEARCH_READ_CONTEXT_MAX_TOKENS
from app.context_preparation import count_tokens
from app.schemas.tools import SearchResult


URL = "https://example.com/research"


def test_research_bounds_read_content_before_storing_it():
    state = SimpleNamespace(
        search_results=[
            SearchResult(
                title="Research source",
                url=URL,
                snippet="Useful source.",
            )
        ],
        visited_urls=[],
        read_sources=[],
        read_count=0,
        steps=0,
        last_error=None,
    )

    action = SimpleNamespace(url=URL)

    result = _execute_read(
        state=state,
        action=action,
        read_tool=lambda url: (
            "agentic supply chain evidence " * 5000
        ),
    )

    assert len(result.read_sources) == 1
    assert (
        count_tokens(result.read_sources[0].content)
        <= RESEARCH_READ_CONTEXT_MAX_TOKENS
    )
    assert result.last_error is None
