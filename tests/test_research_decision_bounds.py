import pytest

from app.agents.research import (
    MAX_RESEARCH_DECISIONS,
    run_research_loop,
)
from app.schemas.opportunity import OpportunityEvaluation
from app.schemas.post import PostCandidate
from app.schemas.research import (
    ResearchAction,
    ResearchActionType,
    ResearchObjective,
    ResearchState,
    ResearchStatus,
)
from app.schemas.tools import SearchResult


@pytest.fixture
def research_state() -> ResearchState:
    return ResearchState(
        post=PostCandidate(
            post_id="post-001",
            post_text="AI agents may transform supply chain planning.",
            post_url="https://example.com/post",
            author_name="Test Author",
        ),
        opportunity_evaluation=OpportunityEvaluation(
            topic_relevance=90,
            positioning_fit=85,
            contribution_potential=95,
            research_cost=40,
            engagement_potential=50,
            research_efficiency=60,
            opportunity_score=82.0,
            classification="HIGH",
        ),
    )


def objective_builder(_: ResearchState) -> ResearchObjective:
    return ResearchObjective(
        question="How can AI agents support supply chain planning?",
        focus_areas=["planning automation", "human oversight"],
    )


def fake_search(_: str) -> list[SearchResult]:
    return []


def fake_read(_: str) -> str:
    return "unused"


def test_research_loop_stops_after_maximum_decision_attempts(
    research_state: ResearchState,
) -> None:
    def invalid_action_decider(_: ResearchState) -> ResearchAction:
        return ResearchAction(
            action=ResearchActionType.READ,
            url="https://example.com/not-discovered",
            reason="Keep requesting an invalid URL.",
        )

    result = run_research_loop(
        state=research_state,
        objective_builder=objective_builder,
        action_decider=invalid_action_decider,
        search_tool=fake_search,
        read_tool=fake_read,
    )

    assert result.status == ResearchStatus.LIMIT_REACHED
    assert result.decision_attempts == MAX_RESEARCH_DECISIONS
    assert result.steps == 0
    assert result.last_error == "Maximum research decisions reached."


def test_decision_attempts_count_valid_and_invalid_decisions(
    research_state: ResearchState,
) -> None:
    decisions = iter(
        [
            ResearchAction(
                action=ResearchActionType.READ,
                url="https://example.com/not-discovered",
                reason="Invalid first attempt.",
            ),
            ResearchAction(
                action=ResearchActionType.FINISH,
                finish_status=ResearchStatus.INSUFFICIENT,
                reason="Stop after recovering.",
            ),
        ]
    )

    def action_decider(_: ResearchState) -> ResearchAction:
        return next(decisions)

    result = run_research_loop(
        state=research_state,
        objective_builder=objective_builder,
        action_decider=action_decider,
        search_tool=fake_search,
        read_tool=fake_read,
    )

    assert result.status == ResearchStatus.INSUFFICIENT
    assert result.decision_attempts == 2
    assert result.steps == 1
    assert result.last_error is None


def test_decision_limit_does_not_replace_operational_step_limit(
    research_state: ResearchState,
) -> None:
    def action_decider(state: ResearchState) -> ResearchAction:
        if state.steps < 9:
            return ResearchAction(
                action=ResearchActionType.EXTRACT,
                reason="Invalid extract keeps decision count moving.",
            )

        return ResearchAction(
            action=ResearchActionType.FINISH,
            finish_status=ResearchStatus.INSUFFICIENT,
            reason="Finish.",
        )

    result = run_research_loop(
        state=research_state,
        objective_builder=objective_builder,
        action_decider=action_decider,
        search_tool=fake_search,
        read_tool=fake_read,
    )

    assert result.status == ResearchStatus.LIMIT_REACHED
    assert result.decision_attempts == MAX_RESEARCH_DECISIONS
    assert result.steps == 0
