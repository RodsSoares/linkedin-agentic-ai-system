import pytest
from pydantic import ValidationError

from app.schemas.opportunity import OpportunityEvaluation
from app.schemas.post import PostCandidate
from app.schemas.research import (
    EvidenceItem,
    ReadSource,
    ResearchAction,
    ResearchActionType,
    ResearchBrief,
    ResearchObjective,
    ResearchState,
    ResearchStatus,
)
from app.schemas.tools import SearchResult


@pytest.fixture
def post_candidate() -> PostCandidate:
    return PostCandidate(
        post_id="test-post-001",
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
        question=(
            "To what extent can AI agents automate supply chain planning "
            "while still requiring human judgment?"
        ),
        focus_areas=[
            "planning activities that can be automated",
            "activities requiring human judgment",
            "limitations of autonomous planning agents",
        ],
    )


@pytest.fixture
def evidence_item() -> EvidenceItem:
    return EvidenceItem(
        claim=(
            "AI systems can automate portions of planning while human "
            "judgment remains important for ambiguous exceptions."
        ),
        support=(
            "The observed source describes automated planning support "
            "combined with human review for exceptional situations."
        ),
        source_url="https://example.com/source",
        source_title="AI and Supply Chain Planning",
        relevance=95,
        confidence=90,
    )


def test_research_objective_accepts_valid_data(
    research_objective: ResearchObjective,
) -> None:
    assert research_objective.question
    assert len(research_objective.focus_areas) == 3


def test_research_objective_rejects_empty_question() -> None:
    with pytest.raises(ValidationError):
        ResearchObjective(
            question="",
            focus_areas=["human judgment"],
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("relevance", -1),
        ("relevance", 101),
        ("confidence", -1),
        ("confidence", 101),
    ],
)
def test_evidence_item_rejects_scores_outside_valid_range(
    field: str,
    value: int,
    evidence_item: EvidenceItem,
) -> None:
    payload = evidence_item.model_dump()
    payload[field] = value

    with pytest.raises(ValidationError):
        EvidenceItem(**payload)


def test_evidence_item_accepts_boundary_scores(
    evidence_item: EvidenceItem,
) -> None:
    payload = evidence_item.model_dump()
    payload["relevance"] = 0
    payload["confidence"] = 100

    evidence = EvidenceItem(**payload)

    assert evidence.relevance == 0
    assert evidence.confidence == 100


@pytest.mark.parametrize(
    "action_type",
    list(ResearchActionType),
)
def test_research_action_accepts_supported_action_types(
    action_type: ResearchActionType,
) -> None:
    action = ResearchAction(
        action=action_type,
        reason="Test action.",
    )

    assert action.action == action_type


def test_research_action_accepts_finish_status() -> None:
    action = ResearchAction(
        action=ResearchActionType.FINISH,
        finish_status=ResearchStatus.INSUFFICIENT,
        reason="Research objective remains unsupported.",
    )

    assert action.finish_status == ResearchStatus.INSUFFICIENT


def test_research_action_rejects_unsupported_action() -> None:
    with pytest.raises(ValidationError):
        ResearchAction(
            action="DELETE_THE_INTERNET",
            reason="Unsupported action.",
        )


def test_research_action_rejects_empty_reason() -> None:
    with pytest.raises(ValidationError):
        ResearchAction(
            action=ResearchActionType.SEARCH,
            search_query="AI supply chain",
            reason="",
        )


def test_read_source_accepts_valid_data() -> None:
    source = ReadSource(
        url="https://example.com/source",
        title="AI and Supply Chain Planning",
        content="Observed source content about AI planning and human oversight.",
    )

    assert source.url == "https://example.com/source"
    assert source.title == "AI and Supply Chain Planning"
    assert source.content


def test_research_state_accepts_valid_initial_state(
    post_candidate: PostCandidate,
    opportunity_evaluation: OpportunityEvaluation,
) -> None:
    state = ResearchState(
        post=post_candidate,
        opportunity_evaluation=opportunity_evaluation,
    )

    assert state.research_objective is None
    assert state.search_queries == []
    assert state.search_results == []
    assert state.visited_urls == []
    assert state.read_sources == []
    assert state.evidence == []
    assert state.steps == 0
    assert state.search_count == 0
    assert state.read_count == 0
    assert state.last_error is None
    assert state.status is None


def test_research_state_rejects_negative_operational_counters(
    post_candidate: PostCandidate,
    opportunity_evaluation: OpportunityEvaluation,
) -> None:
    with pytest.raises(ValidationError):
        ResearchState(
            post=post_candidate,
            opportunity_evaluation=opportunity_evaluation,
            steps=-1,
        )


@pytest.mark.parametrize(
    "status",
    list(ResearchStatus),
)
def test_research_status_accepts_supported_values(
    status: ResearchStatus,
) -> None:
    assert ResearchStatus(status) == status


def test_research_status_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        ResearchStatus("RUN_FOREVER")


def test_research_brief_accepts_valid_result(
    research_objective: ResearchObjective,
    evidence_item: EvidenceItem,
) -> None:
    source = SearchResult(
        title="AI and Supply Chain Planning",
        url="https://example.com/source",
        snippet="AI planning systems increasingly combine automation and human review.",
    )

    brief = ResearchBrief(
        research_objective=research_objective,
        summary=(
            "AI can automate portions of planning, but human judgment "
            "remains relevant for exceptions and ambiguity."
        ),
        key_findings=[
            "Some planning activities can be automated.",
            "Human oversight remains important in ambiguous cases.",
        ],
        evidence=[evidence_item],
        counterpoints=[
            "Automation capability varies significantly by process and context."
        ],
        unresolved_questions=[
            "The rate of adoption across companies remains uncertain."
        ],
        sources=[source],
        status=ResearchStatus.SUFFICIENT,
    )

    assert brief.status == ResearchStatus.SUFFICIENT
    assert len(brief.evidence) == 1
    assert len(brief.sources) == 1


def test_research_brief_rejects_empty_summary(
    research_objective: ResearchObjective,
) -> None:
    with pytest.raises(ValidationError):
        ResearchBrief(
            research_objective=research_objective,
            summary="",
            status=ResearchStatus.INSUFFICIENT,
        )
        