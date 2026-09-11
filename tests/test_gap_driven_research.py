from app.agents.research import execute_research_action
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


def make_post() -> PostCandidate:
    return PostCandidate(
        post_id="post-001",
        post_text="Agentic AI can execute bounded supply-chain workflows.",
        post_url="https://example.com/post",
        author_name="Test Author",
        source="linkedin",
    )


def make_opportunity() -> OpportunityEvaluation:
    return OpportunityEvaluation(
        topic_relevance=90,
        positioning_fit=90,
        contribution_potential=90,
        research_cost=30,
        engagement_potential=50,
        research_efficiency=70,
        opportunity_score=85.0,
        classification="HIGH",
    )


def make_evidence() -> EvidenceItem:
    return EvidenceItem(
        claim="Bounded autonomy requires explicit governance controls.",
        support="The source describes explicit governance and oversight controls.",
        source_url="https://example.com/source-1",
        source_title="Source One",
        relevance=95,
        confidence=95,
    )


def make_state(*, with_evidence: bool = True) -> ResearchState:
    return ResearchState(
        post=make_post(),
        opportunity_evaluation=make_opportunity(),
        research_objective=ResearchObjective(
            question="What controls make bounded agentic execution defensible?",
            focus_areas=["governance", "operational metrics"],
        ),
        evidence=[make_evidence()] if with_evidence else [],
    )


def fake_search(query: str) -> list[SearchResult]:
    return [
        SearchResult(
            title="Source Two",
            url="https://example.com/source-2",
            snippet=f"Result for {query}",
        )
    ]


def fake_read(url: str) -> str:
    return f"Observed content from {url}"


def test_research_action_accepts_gap_driven_semantic_fields() -> None:
    action = ResearchAction(
        action=ResearchActionType.SEARCH,
        search_query="bounded AI rollback operational evidence",
        material_gaps=[
            "The current evidence does not establish operational rollback behavior."
        ],
        next_research_goal=(
            "Find credible evidence describing rollback or recovery controls."
        ),
        sufficiency_reason=(
            "Current governance evidence is useful, but rollback remains material."
        ),
        reason="Resolve the remaining rollback-control gap.",
    )

    assert len(action.material_gaps) == 1
    assert action.next_research_goal is not None
    assert action.sufficiency_reason is not None


def test_additional_search_after_evidence_requires_material_gap() -> None:
    state = make_state()
    action = ResearchAction(
        action=ResearchActionType.SEARCH,
        search_query="more agentic AI evidence",
        reason="Search for another source.",
    )

    updated = execute_research_action(
        state=state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_read,
    )

    assert updated.search_count == 0
    assert updated.steps == 0
    assert updated.last_error == (
        "SEARCH after evidence extraction requires at least one explicit material gap."
    )


def test_additional_search_after_evidence_requires_specific_goal() -> None:
    state = make_state()
    action = ResearchAction(
        action=ResearchActionType.SEARCH,
        search_query="agentic AI rollback evidence",
        material_gaps=["Rollback behavior remains unsupported."],
        reason="Resolve the rollback gap.",
    )

    updated = execute_research_action(
        state=state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_read,
    )

    assert updated.search_count == 0
    assert updated.steps == 0
    assert updated.last_error == (
        "SEARCH after evidence extraction requires a specific next_research_goal."
    )


def test_gap_targeted_search_after_evidence_is_allowed() -> None:
    state = make_state()
    action = ResearchAction(
        action=ResearchActionType.SEARCH,
        search_query="agentic AI rollback recovery controls",
        material_gaps=["Rollback behavior remains unsupported."],
        next_research_goal="Find evidence for rollback or recovery controls.",
        sufficiency_reason="One material operational-safety gap remains.",
        reason="Resolve the rollback gap with a targeted search.",
    )

    updated = execute_research_action(
        state=state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_read,
    )

    assert updated.search_count == 1
    assert updated.steps == 1
    assert updated.last_error is None
    assert updated.search_results[0].url == "https://example.com/source-2"


def test_finish_preserves_semantic_sufficiency_reason_and_clears_goal() -> None:
    state = make_state()
    state.material_gaps = []
    state.next_research_goal = "Old goal that is no longer material."

    action = ResearchAction(
        action=ResearchActionType.FINISH,
        finish_status=ResearchStatus.SUFFICIENT,
        material_gaps=[],
        next_research_goal=None,
        sufficiency_reason=(
            "The extracted evidence now supports one defensible contribution."
        ),
        reason="No material evidence gap remains.",
    )

    updated = execute_research_action(
        state=state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_read,
    )

    assert updated.status == ResearchStatus.SUFFICIENT
    assert updated.sufficiency_reason == (
        "The extracted evidence now supports one defensible contribution."
    )
    assert updated.next_research_goal is None


def test_finish_remains_backward_compatible_with_action_reason() -> None:
    state = make_state()
    action = ResearchAction(
        action=ResearchActionType.FINISH,
        finish_status=ResearchStatus.SUFFICIENT,
        reason="Existing evidence is sufficient.",
    )

    updated = execute_research_action(
        state=state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_read,
    )

    assert updated.status == ResearchStatus.SUFFICIENT
    assert updated.sufficiency_reason == "Existing evidence is sufficient."
    