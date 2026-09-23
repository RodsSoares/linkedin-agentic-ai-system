from types import SimpleNamespace
from unittest.mock import patch

from app.agents.research import execute_research_action
from app.agents.research_llm import (
    build_research_brief_with_llm,
    build_research_objective_with_llm,
    decide_research_action_with_llm,
)
from app.agents.scout import decide_next_action, execute_action
from app.components.evaluator import evaluator
from app.components.opportunity_evaluator import evaluate_opportunity_semantics
from app.components.writer import writer
from app.schemas.evaluator import (
    EvaluationSignals,
    EvaluatorInput,
    VoiceEvaluation,
)
from app.schemas.opportunity import (
    OpportunityEvaluation,
    OpportunitySignals,
)
from app.schemas.post import PostCandidate
from app.schemas.research import (
    EvidenceItem,
    ResearchAction,
    ResearchActionType,
    ResearchBrief,
    ResearchBriefSynthesis,
    ResearchObjective,
    ResearchState,
    ResearchStatus,
)
from app.schemas.scout import ScoutAction, ScoutState
from app.schemas.tools import SearchResult
from app.schemas.writer import WriterInput
from app.telemetry.usage import capture_usage


def make_usage(
    *,
    input_tokens: int = 100,
    output_tokens: int = 20,
    total_tokens: int = 120,
):
    return SimpleNamespace(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        input_tokens_details=SimpleNamespace(cached_tokens=0),
        output_tokens_details=SimpleNamespace(reasoning_tokens=0),
    )


def make_response(*, parsed=None, output_text="draft"):
    return SimpleNamespace(
        output_parsed=parsed,
        output_text=output_text,
        usage=make_usage(),
    )


def make_post() -> PostCandidate:
    return PostCandidate(
        post_id="post-1",
        author_name="Test Author",
        post_text="A short post about AI and supply chain.",
        post_url="https://example.com/post-1",
    )


def make_opportunity_signals() -> OpportunitySignals:
    return OpportunitySignals(
        topic_relevance=90,
        positioning_fit=90,
        contribution_potential=90,
        research_cost=20,
    )


def make_opportunity_evaluation() -> OpportunityEvaluation:
    return OpportunityEvaluation(
        topic_relevance=90,
        positioning_fit=90,
        contribution_potential=90,
        engagement_potential=50,
        research_cost=20,
        research_efficiency=80,
        opportunity_score=85.0,
        classification="HIGH",
    )


def make_research_objective() -> ResearchObjective:
    return ResearchObjective(
        question="What evidence supports the main claim?",
        focus_areas=["evidence"],
    )


def make_evidence() -> EvidenceItem:
    return EvidenceItem(
        claim="A relevant factual claim.",
        support="Supporting evidence.",
        source_url="https://example.com/source",
        source_title="Example Source",
        relevance=95,
        confidence=95,
    )


def make_research_brief() -> ResearchBrief:
    return ResearchBrief(
        research_objective=make_research_objective(),
        summary="Short summary.",
        key_findings=["Finding 1"],
        evidence=[make_evidence()],
        counterpoints=[],
        unresolved_questions=[],
        sources=[],
        status=ResearchStatus.SUFFICIENT,
    )


def test_scout_records_llm_usage():
    state = ScoutState(objective="Find relevant posts")

    response = make_response(
        parsed=ScoutAction(
            action="FINISH",
            reason="Enough exploration for this test.",
        )
    )

    with patch(
        "app.agents.scout.client.responses.parse",
        return_value=response,
    ):
        with capture_usage() as usage:
            action = decide_next_action(state)

    assert action.action == "FINISH"
    assert len(usage.llm_records) == 1

    record = usage.llm_records[0]
    assert record.component == "scout"
    assert record.operation == "decide_next_action"
    assert record.total_tokens == 120
    assert record.latency_ms is not None


def test_opportunity_records_llm_usage():
    response = make_response(
        parsed=make_opportunity_signals()
    )

    with patch(
        "app.components.opportunity_evaluator.client.responses.parse",
        return_value=response,
    ):
        with capture_usage() as usage:
            result = evaluate_opportunity_semantics(make_post())

    assert result.topic_relevance == 90
    assert len(usage.llm_records) == 1

    record = usage.llm_records[0]
    assert record.component == "opportunity"
    assert record.operation == "evaluate"
    assert record.total_tokens == 120
    assert record.latency_ms is not None


def test_research_objective_records_distinct_operation():
    llm = SimpleNamespace(
        responses=SimpleNamespace(
            parse=lambda **kwargs: make_response(
                parsed=make_research_objective()
            )
        )
    )

    state = ResearchState(
        post=make_post(),
        opportunity_evaluation=make_opportunity_evaluation(),
    )

    with capture_usage() as usage:
        result = build_research_objective_with_llm(
            state=state,
            llm=llm,
        )

    assert result.question
    assert len(usage.llm_records) == 1

    record = usage.llm_records[0]
    assert record.component == "research"
    assert record.operation == "build_objective"
    assert record.total_tokens == 120
    assert record.latency_ms is not None


def test_research_action_records_distinct_operation():
    action = ResearchAction(
        action=ResearchActionType.FINISH,
        finish_status=ResearchStatus.INSUFFICIENT,
        reason="No further evidence is needed for this instrumentation test.",
    )

    llm = SimpleNamespace(
        responses=SimpleNamespace(
            parse=lambda **kwargs: make_response(parsed=action)
        )
    )

    state = ResearchState(
        post=make_post(),
        opportunity_evaluation=make_opportunity_evaluation(),
        research_objective=make_research_objective(),
    )

    with capture_usage() as usage:
        result = decide_research_action_with_llm(
            state=state,
            llm=llm,
        )

    assert result.action == ResearchActionType.FINISH
    assert len(usage.llm_records) == 1

    record = usage.llm_records[0]
    assert record.component == "research"
    assert record.operation == "decide_action"
    assert record.total_tokens == 120
    assert record.latency_ms is not None


def test_research_brief_records_distinct_operation():
    synthesis = ResearchBriefSynthesis(
        summary="Summary",
        key_findings=["Finding"],
        counterpoints=[],
        unresolved_questions=[],
    )

    llm = SimpleNamespace(
        responses=SimpleNamespace(
            parse=lambda **kwargs: make_response(parsed=synthesis)
        )
    )

    state = ResearchState(
        post=make_post(),
        opportunity_evaluation=make_opportunity_evaluation(),
        research_objective=make_research_objective(),
        evidence=[make_evidence()],
        status=ResearchStatus.SUFFICIENT,
    )

    with capture_usage() as usage:
        result = build_research_brief_with_llm(
            state=state,
            llm=llm,
        )

    assert result.status == ResearchStatus.SUFFICIENT
    assert len(usage.llm_records) == 1

    record = usage.llm_records[0]
    assert record.component == "research"
    assert record.operation == "build_brief"
    assert record.total_tokens == 120
    assert record.latency_ms is not None


def test_writer_records_llm_usage():
    input_data = WriterInput(
        post=make_post(),
        research_result=make_research_brief(),
        previous_draft=None,
        revision_instruction=None,
    )

    response = make_response(output_text="Useful draft")

    with patch(
        "app.components.writer.client.responses.create",
        return_value=response,
    ):
        with capture_usage() as usage:
            result = writer(input_data)

    assert result == "Useful draft"
    assert len(usage.llm_records) == 1

    record = usage.llm_records[0]
    assert record.component == "writer"
    assert record.operation == "draft"
    assert record.total_tokens == 120
    assert record.latency_ms is not None


def test_evaluator_records_llm_usage():
    signals = EvaluationSignals(
        factual_accuracy=95,
        relevance=95,
        revision_instruction=None,
        voice=VoiceEvaluation(
            naturalness=90,
            directness=90,
            practical_insight=90,
            professional_maturity=90,
            business_technology_fit=90,
            anti_cliche=90,
            non_promotional=90,
        ),
    )

    response = make_response(parsed=signals)

    input_data = EvaluatorInput(
        post=make_post(),
        current_draft="Useful draft",
        research_result=make_research_brief(),
    )

    with patch(
        "app.components.evaluator.client.responses.parse",
        return_value=response,
    ):
        with capture_usage() as usage:
            result = evaluator(input_data)

    assert result.decision == "PASS"
    assert len(usage.llm_records) == 1

    record = usage.llm_records[0]
    assert record.component == "evaluator"
    assert record.operation == "evaluate"
    assert record.total_tokens == 120
    assert record.latency_ms is not None


def test_scout_read_records_context_usage():
    state = ScoutState(
        objective="Find relevant posts",
        search_results=[
            SearchResult(
                title="Example",
                url="https://example.com/article",
                snippet="Example snippet",
            )
        ],
    )

    action = ScoutAction(
        action="READ",
        url="https://example.com/article",
        reason="Read the discovered article.",
    )

    with patch(
        "app.agents.scout.prepare_context",
        return_value=SimpleNamespace(
            content="prepared content",
            original_tokens=3000,
            prepared_tokens=1800,
            truncated=True,
        ),
    ):
        with capture_usage() as usage:
            result = execute_action(
                action=action,
                state=state,
                search_tool=lambda query: [],
                read_tool=lambda url: "raw content",
            )

    assert result == "prepared content"
    assert len(usage.context_records) == 1

    record = usage.context_records[0]
    assert record.component == "scout"
    assert record.operation == "read_context"
    assert record.original_tokens == 3000
    assert record.prepared_tokens == 1800
    assert record.truncated is True


def test_research_read_records_context_usage():
    state = ResearchState(
        post=make_post(),
        opportunity_evaluation=make_opportunity_evaluation(),
        research_objective=make_research_objective(),
        search_results=[
            SearchResult(
                title="Example Source",
                url="https://example.com/source",
                snippet="Example snippet",
            )
        ],
    )

    action = ResearchAction(
        action=ResearchActionType.READ,
        url="https://example.com/source",
        reason="Read the discovered source.",
    )

    with patch(
        "app.agents.research.prepare_context",
        return_value=SimpleNamespace(
            content="prepared research content",
            original_tokens=4200,
            prepared_tokens=2500,
            truncated=True,
        ),
    ):
        with capture_usage() as usage:
            result = execute_research_action(
                state=state,
                action=action,
                search_tool=lambda query: [],
                read_tool=lambda url: "raw content",
            )

    assert result.read_count == 1
    assert len(usage.context_records) == 1

    record = usage.context_records[0]
    assert record.component == "research"
    assert record.operation == "read_context"
    assert record.original_tokens == 4200
    assert record.prepared_tokens == 2500
    assert record.truncated is True
