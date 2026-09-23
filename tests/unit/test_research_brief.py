import pytest

from app.agents.research import build_research_brief
from app.schemas.opportunity import OpportunityEvaluation
from app.schemas.post import PostCandidate
from app.schemas.research import (
    EvidenceItem,
    ResearchBrief,
    ResearchBriefSynthesis,
    ResearchObjective,
    ResearchState,
    ResearchStatus,
)
from app.schemas.tools import SearchResult


@pytest.fixture
def research_objective() -> ResearchObjective:
    return ResearchObjective(
        question="How can AI agents support supply chain planning?",
        focus_areas=["automation", "human judgment"],
    )


@pytest.fixture
def evidence_item() -> EvidenceItem:
    return EvidenceItem(
        claim="AI can automate portions of supply chain planning.",
        support=(
            "The source states that AI can automate some planning tasks "
            "while human oversight remains important."
        ),
        source_url="https://example.com/source",
        source_title="AI Supply Chain Research",
        relevance=95,
        confidence=90,
    )


@pytest.fixture
def completed_state(
    research_objective: ResearchObjective,
    evidence_item: EvidenceItem,
) -> ResearchState:
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
        research_objective=research_objective,
        search_queries=["AI supply chain planning"],
        search_results=[
            SearchResult(
                title="AI Supply Chain Research",
                url="https://example.com/source",
                snippet="Relevant result.",
            )
        ],
        evidence=[evidence_item],
        steps=4,
        search_count=1,
        read_count=1,
        status=ResearchStatus.SUFFICIENT,
    )


def make_synthesis(
    summary: str = "Research summary.",
) -> ResearchBriefSynthesis:
    return ResearchBriefSynthesis(
        summary=summary,
        key_findings=["Finding A"],
        counterpoints=["Counterpoint A"],
        unresolved_questions=["Question A"],
    )


def test_build_research_brief_returns_structured_brief(
    completed_state: ResearchState,
) -> None:
    def brief_builder(state: ResearchState) -> ResearchBriefSynthesis:
        return ResearchBriefSynthesis(
            summary=(
                "AI can automate portions of supply chain planning, "
                "but human judgment remains important."
            ),
            key_findings=[
                "Some planning activities can be automated.",
                "Human oversight remains important for ambiguity.",
            ],
            counterpoints=[
                "Automation capability varies by process and context."
            ],
            unresolved_questions=[
                "The rate of adoption across companies remains uncertain."
            ],
        )

    brief = build_research_brief(
        state=completed_state,
        brief_builder=brief_builder,
    )

    assert isinstance(brief, ResearchBrief)
    assert brief.status == ResearchStatus.SUFFICIENT
    assert len(brief.evidence) == 1
    assert len(brief.sources) == 1


def test_build_research_brief_preserves_runtime_owned_fields(
    completed_state: ResearchState,
) -> None:
    expected_objective = completed_state.research_objective
    expected_evidence = list(completed_state.evidence)
    expected_sources = list(completed_state.search_results)
    expected_status = completed_state.status

    brief = build_research_brief(
        state=completed_state,
        brief_builder=lambda state: make_synthesis(),
    )

    assert brief.research_objective == expected_objective
    assert brief.evidence == expected_evidence
    assert brief.sources == expected_sources
    assert brief.status == expected_status


def test_build_research_brief_uses_only_synthesis_fields_from_builder(
    completed_state: ResearchState,
) -> None:
    synthesis = ResearchBriefSynthesis(
        summary="LLM-owned summary.",
        key_findings=["LLM-owned finding."],
        counterpoints=["LLM-owned counterpoint."],
        unresolved_questions=["LLM-owned question."],
    )

    brief = build_research_brief(
        state=completed_state,
        brief_builder=lambda state: synthesis,
    )

    assert brief.summary == synthesis.summary
    assert brief.key_findings == synthesis.key_findings
    assert brief.counterpoints == synthesis.counterpoints
    assert brief.unresolved_questions == synthesis.unresolved_questions


def test_build_research_brief_rejects_state_without_objective(
    completed_state: ResearchState,
) -> None:
    completed_state.research_objective = None

    def brief_builder(state: ResearchState) -> ResearchBriefSynthesis:
        raise AssertionError("Builder must not be called.")

    with pytest.raises(ValueError):
        build_research_brief(
            state=completed_state,
            brief_builder=brief_builder,
        )


def test_build_research_brief_rejects_unfinished_state(
    completed_state: ResearchState,
) -> None:
    completed_state.status = None

    def brief_builder(state: ResearchState) -> ResearchBriefSynthesis:
        raise AssertionError("Builder must not be called.")

    with pytest.raises(ValueError):
        build_research_brief(
            state=completed_state,
            brief_builder=brief_builder,
        )


@pytest.mark.parametrize(
    "status",
    [
        ResearchStatus.SUFFICIENT,
        ResearchStatus.INSUFFICIENT,
        ResearchStatus.LIMIT_REACHED,
    ],
)
def test_build_research_brief_accepts_all_terminal_statuses(
    completed_state: ResearchState,
    status: ResearchStatus,
) -> None:
    completed_state.status = status

    brief = build_research_brief(
        state=completed_state,
        brief_builder=lambda state: make_synthesis(
            "Research completed with a terminal status."
        ),
    )

    assert brief.status == status


def test_research_brief_synthesis_cannot_carry_runtime_owned_fields() -> None:
    fields = ResearchBriefSynthesis.model_fields

    assert "research_objective" not in fields
    assert "evidence" not in fields
    assert "sources" not in fields
    assert "status" not in fields
    