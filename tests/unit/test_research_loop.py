from collections.abc import Callable

import pytest

from app.agents.research import (
    initialize_research_objective,
    run_research_loop,
)
from app.schemas.opportunity import OpportunityEvaluation
from app.schemas.post import PostCandidate
from app.schemas.research import (
    EvidenceItem,
    ResearchAction,
    ResearchActionType,
    ResearchObjective,
    ResearchState,
    ResearchStatus,
)
from app.schemas.tools import SearchResult


@pytest.fixture
def post_candidate() -> PostCandidate:
    return PostCandidate(
        post_id="post-001",
        post_text="AI agents may transform supply chain planning.",
        post_url="https://example.com/post",
        author_name="Test Author",
    )


@pytest.fixture
def opportunity_evaluation() -> OpportunityEvaluation:
    return OpportunityEvaluation(
        topic_relevance=90,
        positioning_fit=85,
        contribution_potential=95,
        research_cost=40,
        engagement_potential=50,
        research_efficiency=60,
        opportunity_score=82.0,
        classification="HIGH",
    )


@pytest.fixture
def research_objective() -> ResearchObjective:
    return ResearchObjective(
        question="How can AI agents support supply chain planning?",
        focus_areas=["automation", "human judgment"],
    )


@pytest.fixture
def research_state(
    post_candidate: PostCandidate,
    opportunity_evaluation: OpportunityEvaluation,
) -> ResearchState:
    return ResearchState(
        post=post_candidate,
        opportunity_evaluation=opportunity_evaluation,
    )


def fake_search(query: str) -> list[SearchResult]:
    return [
        SearchResult(
            title="AI Supply Chain Research",
            url="https://example.com/source",
            snippet=f"Result for query: {query}",
        )
    ]


def fake_reader(url: str) -> str:
    return (
        "AI can automate some planning tasks while human oversight "
        "remains important for ambiguous exceptions."
    )


def test_initialize_research_objective_sets_objective_once(
    research_state: ResearchState,
    research_objective: ResearchObjective,
) -> None:
    calls = 0

    def objective_builder(state: ResearchState) -> ResearchObjective:
        nonlocal calls
        calls += 1
        return research_objective

    updated = initialize_research_objective(
        state=research_state,
        objective_builder=objective_builder,
    )

    assert updated.research_objective == research_objective
    assert calls == 1


def test_initialize_research_objective_does_not_overwrite_existing_objective(
    research_state: ResearchState,
    research_objective: ResearchObjective,
) -> None:
    research_state.research_objective = research_objective

    calls = 0

    def objective_builder(state: ResearchState) -> ResearchObjective:
        nonlocal calls
        calls += 1
        return ResearchObjective(
            question="This objective must not replace the existing one.",
            focus_areas=["wrong"],
        )

    updated = initialize_research_objective(
        state=research_state,
        objective_builder=objective_builder,
    )

    assert updated.research_objective == research_objective
    assert calls == 0


def test_run_research_loop_completes_search_read_extract_finish_sequence(
    research_state: ResearchState,
    research_objective: ResearchObjective,
) -> None:
    actions = iter(
        [
            ResearchAction(
                action=ResearchActionType.SEARCH,
                search_query="AI supply chain planning",
                reason="Find relevant sources.",
            ),
            ResearchAction(
                action=ResearchActionType.READ,
                url="https://example.com/source",
                reason="Read the discovered source.",
            ),
            ResearchAction(
                action=ResearchActionType.EXTRACT,
                evidence=EvidenceItem(
                    claim="AI can automate portions of supply chain planning.",
                    support=(
                        "The source states that AI can automate some planning "
                        "tasks while human oversight remains important."
                    ),
                    source_url="https://example.com/source",
                    source_title="AI Supply Chain Research",
                    relevance=95,
                    confidence=90,
                ),
                reason="Record supported evidence.",
            ),
            ResearchAction(
                action=ResearchActionType.FINISH,
                finish_status=ResearchStatus.SUFFICIENT,
                reason="The minimum evidence required for the Writer is available.",
            ),
        ]
    )

    def objective_builder(state: ResearchState) -> ResearchObjective:
        return research_objective

    def action_decider(state: ResearchState) -> ResearchAction:
        return next(actions)

    updated = run_research_loop(
        state=research_state,
        objective_builder=objective_builder,
        action_decider=action_decider,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.research_objective == research_objective
    assert updated.status == ResearchStatus.SUFFICIENT
    assert updated.search_count == 1
    assert updated.read_count == 1
    assert len(updated.read_sources) == 1
    assert len(updated.evidence) == 1
    assert updated.steps == 4
    assert updated.last_error is None


def test_run_research_loop_allows_recovery_after_blocked_action(
    research_state: ResearchState,
    research_objective: ResearchObjective,
) -> None:
    actions = iter(
        [
            ResearchAction(
                action=ResearchActionType.READ,
                url="https://example.com/source",
                reason="Try to read before discovery.",
            ),
            ResearchAction(
                action=ResearchActionType.SEARCH,
                search_query="AI supply chain planning",
                reason="Discover a valid source.",
            ),
            ResearchAction(
                action=ResearchActionType.READ,
                url="https://example.com/source",
                reason="Read the discovered source.",
            ),
            ResearchAction(
                action=ResearchActionType.EXTRACT,
                evidence=EvidenceItem(
                    claim="AI can automate portions of supply chain planning.",
                    support="The source describes partial planning automation.",
                    source_url="https://example.com/source",
                    source_title="AI Supply Chain Research",
                    relevance=90,
                    confidence=85,
                ),
                reason="Record supported evidence.",
            ),
            ResearchAction(
                action=ResearchActionType.FINISH,
                finish_status=ResearchStatus.SUFFICIENT,
                reason="Usable evidence has been collected.",
            ),
        ]
    )

    def objective_builder(state: ResearchState) -> ResearchObjective:
        return research_objective

    def action_decider(state: ResearchState) -> ResearchAction:
        return next(actions)

    updated = run_research_loop(
        state=research_state,
        objective_builder=objective_builder,
        action_decider=action_decider,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.status == ResearchStatus.SUFFICIENT
    assert updated.search_count == 1
    assert updated.read_count == 1
    assert len(updated.evidence) == 1
    assert updated.steps == 4
    assert updated.last_error is None


def test_run_research_loop_stops_when_finish_is_insufficient(
    research_state: ResearchState,
    research_objective: ResearchObjective,
) -> None:
    def objective_builder(state: ResearchState) -> ResearchObjective:
        return research_objective

    def action_decider(state: ResearchState) -> ResearchAction:
        return ResearchAction(
            action=ResearchActionType.FINISH,
            finish_status=ResearchStatus.INSUFFICIENT,
            reason="No reliable evidence can be gathered.",
        )

    updated = run_research_loop(
        state=research_state,
        objective_builder=objective_builder,
        action_decider=action_decider,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.status == ResearchStatus.INSUFFICIENT
    assert updated.steps == 1
    assert updated.evidence == []


def test_run_research_loop_stops_after_operational_limit(
    research_state: ResearchState,
    research_objective: ResearchObjective,
) -> None:
    query_number = 0

    def objective_builder(state: ResearchState) -> ResearchObjective:
        return research_objective

    def action_decider(state: ResearchState) -> ResearchAction:
        nonlocal query_number
        query_number += 1
        return ResearchAction(
            action=ResearchActionType.SEARCH,
            search_query=f"research query {query_number}",
            reason="Continue searching.",
        )

    updated = run_research_loop(
        state=research_state,
        objective_builder=objective_builder,
        action_decider=action_decider,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.status == ResearchStatus.LIMIT_REACHED
    assert updated.last_error is not None
