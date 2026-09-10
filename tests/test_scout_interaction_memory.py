from unittest.mock import Mock, patch

from app.agents.scout import execute_action, run_scout
from app.memory.service import InteractionMemoryService
from app.schemas.scout import ScoutAction, ScoutState
from app.schemas.tools import SearchResult
from app.tools.errors import WebToolError


URL_A = "https://example.com/article-a"
URL_B = "https://example.com/article-b"


def make_result(
    url: str,
    title: str = "Relevant article",
) -> SearchResult:
    return SearchResult(
        title=title,
        url=url,
        snippet="Relevant content about AI and supply chain.",
    )


def test_search_filters_previously_visited_url(tmp_path):
    memory = InteractionMemoryService(
        database_path=tmp_path / "memory.db"
    )
    memory.record_visit(URL_A)

    state = ScoutState(
        objective="Find relevant opportunities."
    )

    search_tool = Mock(
        return_value=[
            make_result(URL_A),
            make_result(URL_B),
        ]
    )

    action = ScoutAction(
        action="SEARCH",
        query="AI supply chain",
        reason="Discover relevant content.",
    )

    results = execute_action(
        action=action,
        state=state,
        search_tool=search_tool,
        read_tool=Mock(),
        memory_service=memory,
    )

    assert [result.url for result in results] == [URL_B]
    assert [result.url for result in state.search_results] == [URL_B]
    assert state.last_search_outcome == "HAS_NOVEL_RESULTS"


def test_search_reports_no_novel_results_when_all_urls_are_known(
    tmp_path,
):
    memory = InteractionMemoryService(
        database_path=tmp_path / "memory.db"
    )
    memory.record_visit(URL_A)

    state = ScoutState(
        objective="Find relevant opportunities."
    )

    search_tool = Mock(
        return_value=[make_result(URL_A)]
    )

    action = ScoutAction(
        action="SEARCH",
        query="AI supply chain",
        reason="Discover relevant content.",
    )

    results = execute_action(
        action=action,
        state=state,
        search_tool=search_tool,
        read_tool=Mock(),
        memory_service=memory,
    )

    assert results == []
    assert state.search_results == []
    assert state.last_search_outcome == "NO_NOVEL_RESULTS"
    assert state.novelty_search_attempts == 1
    assert state.status != "FINISHED"


def test_no_novel_results_finish_at_retry_limit(tmp_path):
    memory = InteractionMemoryService(
        database_path=tmp_path / "memory.db"
    )
    memory.record_visit(URL_A)

    state = ScoutState(
        objective="Find relevant opportunities.",
        max_novelty_search_attempts=2,
    )

    search_tool = Mock(
        return_value=[make_result(URL_A)]
    )

    first_search = ScoutAction(
        action="SEARCH",
        query="AI supply chain",
        reason="First discovery attempt.",
    )

    second_search = ScoutAction(
        action="SEARCH",
        query="agentic planning automation",
        reason="Reformulate after known results.",
    )

    execute_action(
        action=first_search,
        state=state,
        search_tool=search_tool,
        read_tool=Mock(),
        memory_service=memory,
    )

    assert state.status != "FINISHED"
    assert state.novelty_search_attempts == 1

    execute_action(
        action=second_search,
        state=state,
        search_tool=search_tool,
        read_tool=Mock(),
        memory_service=memory,
    )

    assert state.novelty_search_attempts == 2
    assert state.status == "FINISHED"


def test_novel_result_resets_novelty_attempt_counter(tmp_path):
    memory = InteractionMemoryService(
        database_path=tmp_path / "memory.db"
    )
    memory.record_visit(URL_A)

    state = ScoutState(
        objective="Find relevant opportunities.",
        novelty_search_attempts=2,
    )

    search_tool = Mock(
        return_value=[
            make_result(URL_A),
            make_result(URL_B),
        ]
    )

    action = ScoutAction(
        action="SEARCH",
        query="new AI supply chain research",
        reason="Find a novel source.",
    )

    execute_action(
        action=action,
        state=state,
        search_tool=search_tool,
        read_tool=Mock(),
        memory_service=memory,
    )

    assert state.novelty_search_attempts == 0
    assert state.last_search_outcome == "HAS_NOVEL_RESULTS"
    assert [result.url for result in state.search_results] == [URL_B]


def test_search_distinguishes_no_search_results_from_no_novel_results(
    tmp_path,
):
    memory = InteractionMemoryService(
        database_path=tmp_path / "memory.db"
    )

    state = ScoutState(
        objective="Find relevant opportunities."
    )

    action = ScoutAction(
        action="SEARCH",
        query="unlikely query",
        reason="Search for content.",
    )

    results = execute_action(
        action=action,
        state=state,
        search_tool=Mock(return_value=[]),
        read_tool=Mock(),
        memory_service=memory,
    )

    assert results == []
    assert state.last_search_outcome == "NO_SEARCH_RESULTS"
    assert state.novelty_search_attempts == 0


def test_successful_read_is_persisted(tmp_path):
    memory = InteractionMemoryService(
        database_path=tmp_path / "memory.db"
    )

    state = ScoutState(
        objective="Find relevant opportunities.",
        search_results=[make_result(URL_A)],
    )

    action = ScoutAction(
        action="READ",
        url=URL_A,
        reason="Inspect the result.",
    )

    read_tool = Mock(
        return_value=(
            "AI agents can improve supply chain planning "
            "through bounded autonomous execution."
        )
    )

    execute_action(
        action=action,
        state=state,
        search_tool=Mock(),
        read_tool=read_tool,
        memory_service=memory,
    )

    assert memory.has_seen(URL_A)
    assert URL_A in state.visited_urls
    assert state.last_read_url == URL_A


def test_failed_read_is_not_persisted(tmp_path):
    memory = InteractionMemoryService(
        database_path=tmp_path / "memory.db"
    )

    state = ScoutState(
        objective="Find relevant opportunities.",
        search_results=[make_result(URL_A)],
    )

    action = ScoutAction(
        action="READ",
        url=URL_A,
        reason="Inspect the result.",
    )

    def failing_reader(_: str):
        raise WebToolError("Reader failed.")

    try:
        execute_action(
            action=action,
            state=state,
            search_tool=Mock(),
            read_tool=failing_reader,
            memory_service=memory,
        )
    except WebToolError:
        pass
    else:
        raise AssertionError(
            "READ failure should propagate from execute_action."
        )

    assert not memory.has_seen(URL_A)
    assert URL_A not in state.visited_urls
    assert state.last_read_url is None


def test_select_marks_persisted_interaction_as_selected(tmp_path):
    memory = InteractionMemoryService(
        database_path=tmp_path / "memory.db"
    )
    memory.record_visit(URL_A)

    state = ScoutState(
        objective="Find relevant opportunities.",
        search_results=[make_result(URL_A)],
        visited_urls=[URL_A],
        last_read_url=URL_A,
        last_read_content="Useful content about agentic AI.",
    )

    action = ScoutAction(
        action="SELECT",
        reason="This content is valuable.",
        selection={
            "reason": "Strong fit with the target positioning."
        },
    )

    execute_action(
        action=action,
        state=state,
        search_tool=Mock(),
        read_tool=Mock(),
        memory_service=memory,
    )

    record = memory.get(URL_A)

    assert record is not None
    assert record.status.value == "SELECTED"


def test_memory_persists_between_scout_runs(tmp_path):
    database_path = tmp_path / "memory.db"

    first_memory = InteractionMemoryService(
        database_path=database_path
    )

    first_memory.record_visit(URL_A)

    second_memory = InteractionMemoryService(
        database_path=database_path
    )

    state = ScoutState(
        objective="Find relevant opportunities."
    )

    action = ScoutAction(
        action="SEARCH",
        query="AI supply chain",
        reason="Discover content.",
    )

    results = execute_action(
        action=action,
        state=state,
        search_tool=Mock(
            return_value=[
                make_result(URL_A),
                make_result(URL_B),
            ]
        ),
        read_tool=Mock(),
        memory_service=second_memory,
    )

    assert [result.url for result in results] == [URL_B]


def test_run_scout_reformulates_after_no_novel_results(tmp_path):
    memory = InteractionMemoryService(
        database_path=tmp_path / "memory.db"
    )
    memory.record_visit(URL_A)

    actions = [
        ScoutAction(
            action="SEARCH",
            query="AI supply chain",
            reason="Initial discovery.",
        ),
        ScoutAction(
            action="SEARCH",
            query="agentic supply chain execution",
            reason="Reformulate after known results.",
        ),
        ScoutAction(
            action="FINISH",
            reason="Enough exploration.",
        ),
    ]

    search_tool = Mock(
        side_effect=[
            [make_result(URL_A)],
            [make_result(URL_B)],
        ]
    )

    with patch(
        "app.agents.scout.decide_next_action",
        side_effect=actions,
    ):
        state = run_scout(
            objective="Find relevant opportunities.",
            search_tool=search_tool,
            read_tool=Mock(),
            max_steps=5,
            memory_service=memory,
        )

    assert state.status == "FINISHED"
    assert state.steps == 3
    assert state.search_queries == [
        "AI supply chain",
        "agentic supply chain execution",
    ]
    assert state.last_search_outcome == "HAS_NOVEL_RESULTS"
    assert state.novelty_search_attempts == 0
    