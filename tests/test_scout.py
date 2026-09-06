from unittest.mock import patch

from app.agents.scout import execute_action, run_scout
from app.schemas.scout import ScoutAction, ScoutSelection, ScoutState


def test_scout_runs_search_read_finish_loop():
    actions = [
        ScoutAction(
            action="SEARCH",
            query="AI agents supply chain",
            reason="Need to discover relevant content.",
        ),
        ScoutAction(
            action="READ",
            url="https://example.com/posts/ai-agents-supply-chain",
            reason="This result is strongly related to the objective.",
        ),
        ScoutAction(
            action="FINISH",
            reason="Enough relevant content has been inspected.",
        ),
    ]

    with patch(
        "app.agents.scout.decide_next_action",
        side_effect=actions,
    ):
        state = run_scout(
            objective="Find opportunities about AI agents and Supply Chain.",
            max_steps=5,
        )

    assert state.status == "FINISHED"
    assert state.steps == 3

    assert state.search_queries == [
        "AI agents supply chain"
    ]

    assert (
        "https://example.com/posts/ai-agents-supply-chain"
        in state.visited_urls
    )

    assert len(state.search_results) == 3
    assert state.last_read_content is not None
    assert "supply chain" in state.last_read_content.lower()

def test_scout_rejects_undiscovered_url():
    from app.agents.scout import execute_action
    from app.schemas.scout import ScoutState

    state = ScoutState(
        objective="Find relevant opportunities.",
    )

    action = ScoutAction(
        action="READ",
        url="https://invented.example.com/post",
        reason="Attempt to read an undiscovered URL.",
    )

    try:
        execute_action(
            action=action,
            state=state,
        )
    except ValueError as error:
        assert str(error) == (
            "Scout attempted to read a URL that was not discovered."
        )
    else:
        raise AssertionError(
            "Scout should reject an undiscovered URL."
        )

def test_scout_rejects_repeated_search():
    from app.agents.scout import execute_action
    from app.schemas.scout import ScoutState

    state = ScoutState(
        objective="Find relevant opportunities.",
        search_queries=["AI agents supply chain"],
    )

    action = ScoutAction(
        action="SEARCH",
        query="AI agents supply chain",
        reason="Attempt to repeat a previous search.",
    )

    try:
        execute_action(
            action=action,
            state=state,
        )
    except ValueError as error:
        assert str(error) == (
            "Scout attempted to repeat a search query."
        )
    else:
        raise AssertionError(
            "Scout should reject a repeated search query."
        )   

def test_scout_rejects_revisited_url():
    from app.agents.scout import execute_action
    from app.schemas.scout import ScoutState
    from app.schemas.tools import SearchResult

    url = "https://example.com/posts/ai-agents-supply-chain"

    state = ScoutState(
        objective="Find relevant opportunities.",
        search_results=[
            SearchResult(
                title="AI agents are changing supply chain planning",
                url=url,
                snippet="Relevant content about AI agents and supply chain.",
            )
        ],
        visited_urls=[url],
    )

    action = ScoutAction(
        action="READ",
        url=url,
        reason="Attempt to revisit an already inspected URL.",
    )

    try:
        execute_action(
            action=action,
            state=state,
        )
    except ValueError as error:
        assert str(error) == (
            "Scout attempted to revisit a URL."
        )
    else:
        raise AssertionError(
            "Scout should reject a revisited URL."
        )

def test_scout_stops_at_max_steps():
    actions = [
        ScoutAction(
            action="SEARCH",
            query="AI agents supply chain",
            reason="Search for relevant content.",
        ),
        ScoutAction(
            action="SEARCH",
            query="Generative AI business automation",
            reason="Continue exploring relevant content.",
        ),
        ScoutAction(
            action="SEARCH",
            query="This action should never execute",
            reason="Try to continue beyond the limit.",
        ),
    ]

    with patch(
        "app.agents.scout.decide_next_action",
        side_effect=actions,
    ) as mocked_decision:
        state = run_scout(
            objective="Find relevant opportunities.",
            max_steps=2,
        )

    assert state.status == "FINISHED"
    assert state.steps == 2
    assert len(state.search_queries) == 2
    assert mocked_decision.call_count == 2

def test_decide_next_action_returns_structured_scout_action():
    from unittest.mock import Mock

    from app.agents.scout import decide_next_action
    from app.schemas.scout import ScoutState

    state = ScoutState(
        objective="Find relevant opportunities about AI and Supply Chain.",
    )

    expected_action = ScoutAction(
        action="SEARCH",
        query="AI agents supply chain",
        reason="No searches have been performed yet.",
    )

    mock_response = Mock()
    mock_response.output_parsed = expected_action

    with patch(
        "app.agents.scout.client.responses.parse",
        return_value=mock_response,
    ) as mocked_parse:
        action = decide_next_action(state)

    assert action == expected_action
    assert action.action == "SEARCH"
    assert action.query == "AI agents supply chain"

    mocked_parse.assert_called_once()

def test_scout_recovers_after_blocked_action():
    actions = [
        ScoutAction(
            action="SEARCH",
            query="AI agents supply chain",
            reason="Discover relevant content.",
        ),
        ScoutAction(
            action="SEARCH",
            query="AI agents supply chain",
            reason="Repeat the same search.",
        ),
        ScoutAction(
            action="FINISH",
            reason="Finish after receiving guardrail feedback.",
        ),
    ]

    with patch(
        "app.agents.scout.decide_next_action",
        side_effect=actions,
    ):
        state = run_scout(
            objective="Find relevant opportunities.",
            max_steps=5,
        )

    assert state.status == "FINISHED"
    assert state.steps == 3
    assert state.search_queries == [
        "AI agents supply chain"
    ]
    assert state.last_error is None

def test_scout_selects_last_read_content_as_candidate():
    state = ScoutState(
        objective="Find relevant opportunities."
    )

    search_action = ScoutAction(
        action="SEARCH",
        query="AI agents supply chain",
        reason="Discover relevant content.",
    )
    execute_action(search_action, state)

    read_action = ScoutAction(
        action="READ",
        url="https://example.com/posts/ai-agents-supply-chain",
        reason="Inspect relevant content.",
    )
    execute_action(read_action, state)

    select_action = ScoutAction(
        action="SELECT",
        reason="This content is relevant to the objective.",
        selection=ScoutSelection(
            reason="Strong connection between AI agents and supply chain."
        ),
    )
    execute_action(select_action, state)

    assert len(state.candidates) == 1

    candidate = state.candidates[0]

    assert candidate.post_url == (
        "https://example.com/posts/ai-agents-supply-chain"
    )
    assert candidate.post_text == state.last_read_content
    assert candidate.author_name == "Unknown"

def test_decide_next_action_can_return_select_action():
    from unittest.mock import Mock

    from app.agents.scout import decide_next_action

    state = ScoutState(
        objective="Find relevant opportunities.",
        last_read_url=(
            "https://example.com/posts/ai-agents-supply-chain"
        ),
        last_read_content=(
            "AI agents can support supply chain planning "
            "and decision-making."
        ),
    )

    expected_action = ScoutAction(
        action="SELECT",
        reason="The content is relevant to the objective.",
        selection=ScoutSelection(
            reason=(
                "Strong connection between AI agents "
                "and supply chain."
            )
        ),
    )

    mock_response = Mock()
    mock_response.output_parsed = expected_action

    with patch(
        "app.agents.scout.client.responses.parse",
        return_value=mock_response,
    ):
        action = decide_next_action(state)

    assert action.action == "SELECT"
    assert action.selection is not None
    assert (
        action.selection.reason
        == "Strong connection between AI agents and supply chain."
    )