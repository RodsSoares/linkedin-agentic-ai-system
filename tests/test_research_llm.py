from typing import Any

import pytest

from app.agents.research_llm import (
    build_research_brief_with_llm,
    build_research_objective_with_llm,
    decide_research_action_with_llm,
)
from app.schemas.opportunity import OpportunityEvaluation
from app.schemas.post import PostCandidate
from app.schemas.research import (
    EvidenceItem,
    ReadSource,
    ResearchAction,
    ResearchActionType,
    ResearchBrief,
    ResearchBriefSynthesis,
    ResearchObjective,
    ResearchState,
    ResearchStatus,
)
from app.schemas.tools import SearchResult


class FakeOutputText:
    def __init__(self, parsed: Any) -> None:
        self.type = "output_text"
        self.parsed = parsed


class FakeMessage:
    def __init__(self, parsed: Any) -> None:
        self.type = "message"
        self.content = [FakeOutputText(parsed)]


class FakeResponse:
    def __init__(self, parsed: Any) -> None:
        self.output_parsed = parsed
        self.output = [FakeMessage(parsed)]


class FakeResponsesAPI:
    def __init__(self, responses: dict[type, Any]) -> None:
        self.responses = responses
        self.calls: list[dict[str, Any]] = []

    def parse(
        self,
        *,
        model: str,
        input: str,
        text_format: type,
    ) -> FakeResponse:
        self.calls.append(
            {
                "model": model,
                "input": input,
                "text_format": text_format,
            }
        )
        return FakeResponse(self.responses[text_format])


class FakeOpenAIClient:
    def __init__(self, responses: dict[type, Any]) -> None:
        self.responses = FakeResponsesAPI(responses)


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


@pytest.fixture
def research_objective() -> ResearchObjective:
    return ResearchObjective(
        question="How can AI agents support supply chain planning?",
        focus_areas=["planning automation", "human judgment", "limitations"],
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


def test_build_research_objective_uses_openai_responses_parse(
    research_state: ResearchState,
    research_objective: ResearchObjective,
) -> None:
    client = FakeOpenAIClient({ResearchObjective: research_objective})

    result = build_research_objective_with_llm(
        state=research_state,
        llm=client,
    )

    assert result == research_objective
    assert len(client.responses.calls) == 1
    assert client.responses.calls[0]["text_format"] is ResearchObjective


def test_build_research_objective_prompt_contains_context(
    research_state: ResearchState,
    research_objective: ResearchObjective,
) -> None:
    client = FakeOpenAIClient({ResearchObjective: research_objective})

    build_research_objective_with_llm(
        state=research_state,
        llm=client,
    )

    prompt = client.responses.calls[0]["input"]

    assert research_state.post.post_text in prompt
    assert str(research_state.opportunity_evaluation.opportunity_score) in prompt
    assert "exactly one primary research question" in prompt
    assert "only 1 to 3 focus areas" in prompt
    assert "minimum-sufficient research" in prompt
    assert "not exhaustive topic research" in prompt


def test_decide_research_action_uses_openai_responses_parse(
    research_state: ResearchState,
    research_objective: ResearchObjective,
) -> None:
    research_state.research_objective = research_objective

    expected_action = ResearchAction(
        action=ResearchActionType.SEARCH,
        search_query="AI agents supply chain planning human oversight",
        reason="Need external evidence.",
    )

    client = FakeOpenAIClient({ResearchAction: expected_action})

    result = decide_research_action_with_llm(
        state=research_state,
        llm=client,
    )

    assert result == expected_action
    assert client.responses.calls[0]["text_format"] is ResearchAction


def test_decide_research_action_prompt_contains_state(
    research_state: ResearchState,
    research_objective: ResearchObjective,
) -> None:
    research_state.research_objective = research_objective
    research_state.search_queries.append("previous query")
    research_state.last_error = "Previous action was blocked."

    expected_action = ResearchAction(
        action=ResearchActionType.SEARCH,
        search_query="different query",
        reason="Recover from the blocked action.",
    )

    client = FakeOpenAIClient({ResearchAction: expected_action})

    decide_research_action_with_llm(
        state=research_state,
        llm=client,
    )

    prompt = client.responses.calls[0]["input"]

    assert research_objective.question in prompt
    assert "previous query" in prompt
    assert "Previous action was blocked." in prompt
    assert "prefer READ before another SEARCH" in prompt
    assert "prefer EXTRACT before another SEARCH or READ" in prompt
    assert "choose FINISH rather than broadening the research" in prompt
    assert "local action-limit error" in prompt
    assert "SUFFICIENT only when the collected evidence is enough" in prompt
    assert "INSUFFICIENT when useful evidence exists" in prompt
    assert "Partial evidence is not the same as sufficient evidence" in prompt
    assert "Never request LIMIT_REACHED" in prompt
    assert "relevance must be an integer from 0 to 100" in prompt
    assert "confidence must be an integer from 0 to 100" in prompt


def test_decide_research_action_supports_finish_semantic_status(
    research_state: ResearchState,
    research_objective: ResearchObjective,
) -> None:
    research_state.research_objective = research_objective

    expected_action = ResearchAction(
        action=ResearchActionType.FINISH,
        finish_status=ResearchStatus.INSUFFICIENT,
        reason="Important parts of the objective remain unsupported.",
    )

    client = FakeOpenAIClient({ResearchAction: expected_action})

    result = decide_research_action_with_llm(
        state=research_state,
        llm=client,
    )

    assert result == expected_action
    assert result.finish_status == ResearchStatus.INSUFFICIENT


def test_decide_research_action_prompt_contains_read_content(
    research_state: ResearchState,
    research_objective: ResearchObjective,
) -> None:
    research_state.research_objective = research_objective
    research_state.read_sources.append(
        ReadSource(
            url="https://example.com/source",
            title="AI Supply Chain Research",
            content="Observed content about AI planning and human oversight.",
        )
    )

    expected_action = ResearchAction(
        action=ResearchActionType.EXTRACT,
        evidence=EvidenceItem(
            claim="AI can automate portions of planning.",
            support="Observed content supports partial automation.",
            source_url="https://example.com/source",
            source_title="AI Supply Chain Research",
            relevance=90,
            confidence=85,
        ),
        reason="Extract evidence from the source already read.",
    )

    client = FakeOpenAIClient({ResearchAction: expected_action})

    decide_research_action_with_llm(
        state=research_state,
        llm=client,
    )

    prompt = client.responses.calls[0]["input"]

    assert "Observed content about AI planning and human oversight." in prompt
    assert "https://example.com/source" in prompt


def test_build_research_brief_uses_openai_responses_parse(
    research_state: ResearchState,
    research_objective: ResearchObjective,
    evidence_item: EvidenceItem,
) -> None:
    research_state.research_objective = research_objective
    research_state.evidence.append(evidence_item)
    research_state.search_results.append(
        SearchResult(
            title="AI Supply Chain Research",
            url="https://example.com/source",
            snippet="Relevant source.",
        )
    )
    research_state.status = ResearchStatus.SUFFICIENT

    expected_synthesis = ResearchBriefSynthesis(
        summary="AI can automate portions of planning while human judgment remains important.",
        key_findings=["Planning automation is possible in bounded tasks."],
        counterpoints=["Automation capability depends on context."],
        unresolved_questions=["Adoption levels vary."],
    )

    client = FakeOpenAIClient(
        {ResearchBriefSynthesis: expected_synthesis}
    )

    result = build_research_brief_with_llm(
        state=research_state,
        llm=client,
    )

    assert isinstance(result, ResearchBrief)
    assert result.summary == expected_synthesis.summary
    assert result.key_findings == expected_synthesis.key_findings
    assert result.counterpoints == expected_synthesis.counterpoints
    assert result.unresolved_questions == expected_synthesis.unresolved_questions

    # Runtime-owned fields must come directly from ResearchState.
    assert result.research_objective == research_state.research_objective
    assert result.evidence == research_state.evidence
    assert result.sources == research_state.search_results
    assert result.status == research_state.status

    assert client.responses.calls[0]["text_format"] is ResearchBriefSynthesis


def test_build_research_brief_prompt_uses_only_extracted_evidence(
    research_state: ResearchState,
    research_objective: ResearchObjective,
    evidence_item: EvidenceItem,
) -> None:
    research_state.research_objective = research_objective
    research_state.evidence.append(evidence_item)
    research_state.read_sources.append(
        ReadSource(
            url="https://example.com/raw-source",
            title="Raw Read Source",
            content="RAW READ CONTENT MUST NOT REACH THE BRIEF SYNTHESIS.",
        )
    )
    research_state.search_results.append(
        SearchResult(
            title="Discovery Result",
            url="https://example.com/discovery",
            snippet="RAW SEARCH SNIPPET MUST NOT REACH THE BRIEF SYNTHESIS.",
        )
    )
    research_state.status = ResearchStatus.SUFFICIENT

    expected_synthesis = ResearchBriefSynthesis(
        summary="Research summary.",
    )

    client = FakeOpenAIClient(
        {ResearchBriefSynthesis: expected_synthesis}
    )

    build_research_brief_with_llm(
        state=research_state,
        llm=client,
    )

    prompt = client.responses.calls[0]["input"]

    assert evidence_item.claim in prompt
    assert evidence_item.support in prompt
    assert ResearchStatus.SUFFICIENT.value in prompt
    assert "RAW READ CONTENT MUST NOT REACH THE BRIEF SYNTHESIS." not in prompt
    assert "RAW SEARCH SNIPPET MUST NOT REACH THE BRIEF SYNTHESIS." not in prompt
    assert "only extracted EvidenceItem objects may support factual findings" in prompt
    assert "Return only a ResearchBriefSynthesis" in prompt
    assert client.responses.calls[0]["text_format"] is ResearchBriefSynthesis


def test_build_research_brief_prompt_handles_empty_evidence_conservatively(
    research_state: ResearchState,
    research_objective: ResearchObjective,
) -> None:
    research_state.research_objective = research_objective
    research_state.status = ResearchStatus.INSUFFICIENT

    expected_synthesis = ResearchBriefSynthesis(
        summary="No validated evidence was extracted.",
    )
    client = FakeOpenAIClient(
        {ResearchBriefSynthesis: expected_synthesis}
    )

    build_research_brief_with_llm(
        state=research_state,
        llm=client,
    )

    prompt = client.responses.calls[0]["input"]

    assert "EXTRACTED EVIDENCE ONLY:\nNone" in prompt
    assert (
        "if no EvidenceItem exists, explicitly state that the bounded research did not"
        in prompt
    )


def test_build_research_brief_rejects_missing_objective(
    research_state: ResearchState,
) -> None:
    research_state.status = ResearchStatus.INSUFFICIENT
    client = FakeOpenAIClient({ResearchBriefSynthesis: None})

    with pytest.raises(ValueError):
        build_research_brief_with_llm(
            state=research_state,
            llm=client,
        )


def test_build_research_brief_rejects_unfinished_state(
    research_state: ResearchState,
    research_objective: ResearchObjective,
) -> None:
    research_state.research_objective = research_objective
    research_state.status = None
    client = FakeOpenAIClient({ResearchBriefSynthesis: None})

    with pytest.raises(ValueError):
        build_research_brief_with_llm(
            state=research_state,
            llm=client,
        )
        