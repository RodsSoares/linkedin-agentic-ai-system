import pytest

from app.agents.research import (
    MAX_RESEARCH_EVIDENCE_ITEMS,
    MAX_RESEARCH_READS,
    MAX_RESEARCH_SEARCHES,
    MAX_RESEARCH_STEPS,
    execute_research_action,
)
from app.schemas.opportunity import OpportunityEvaluation
from app.schemas.post import PostCandidate
from app.schemas.research import (
    EvidenceItem,
    ReadSource,
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
        research_objective=ResearchObjective(
            question="How can AI agents support supply chain planning?",
            focus_areas=["automation", "human judgment"],
        ),
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
    return "AI can automate some planning tasks while human oversight remains important."


def make_evidence(
    index: int = 0,
    *,
    source_url: str = "https://example.com/source",
    source_title: str = "AI Supply Chain Research",
) -> EvidenceItem:
    return EvidenceItem(
        claim=f"AI supports planning automation {index}.",
        support=f"Source describes automated planning support {index}.",
        source_url=source_url,
        source_title=source_title,
        relevance=90,
        confidence=85,
    )


def test_search_executes_and_updates_state(
    research_state: ResearchState,
) -> None:
    action = ResearchAction(
        action=ResearchActionType.SEARCH,
        search_query="AI supply chain planning",
        reason="Need supporting evidence.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.search_queries == ["AI supply chain planning"]
    assert len(updated.search_results) == 1
    assert updated.search_count == 1
    assert updated.steps == 1
    assert updated.last_error is None




def test_search_results_are_deduplicated_by_url(
    research_state: ResearchState,
) -> None:
    research_state.search_results.append(
        SearchResult(
            title="Existing result",
            url="https://example.com/source",
            snippet="Previously discovered.",
        )
    )

    def search_with_duplicate(query: str) -> list[SearchResult]:
        return [
            SearchResult(
                title="Duplicate result",
                url="https://example.com/source",
                snippet="Same URL returned again.",
            ),
            SearchResult(
                title="New result",
                url="https://example.com/new-source",
                snippet=f"New result for query: {query}",
            ),
        ]

    action = ResearchAction(
        action=ResearchActionType.SEARCH,
        search_query="new AI supply chain evidence",
        reason="Search for another source.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=search_with_duplicate,
        read_tool=fake_reader,
    )

    assert [result.url for result in updated.search_results] == [
        "https://example.com/source",
        "https://example.com/new-source",
    ]
    assert updated.search_count == 1
    assert updated.steps == 1
    assert updated.last_error is None


def test_repeated_search_is_blocked(
    research_state: ResearchState,
) -> None:
    research_state.search_queries.append("AI supply chain planning")

    action = ResearchAction(
        action=ResearchActionType.SEARCH,
        search_query="AI supply chain planning",
        reason="Repeat search.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.search_count == 0
    assert updated.steps == 0
    assert updated.last_error is not None


def test_read_requires_discovered_url(
    research_state: ResearchState,
) -> None:
    action = ResearchAction(
        action=ResearchActionType.READ,
        url="https://unknown.com/source",
        reason="Read source.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.read_count == 0
    assert updated.last_error is not None


def test_read_executes_for_discovered_url(
    research_state: ResearchState,
) -> None:
    research_state.search_results.append(
        SearchResult(
            title="AI Supply Chain Research",
            url="https://example.com/source",
            snippet="Relevant result.",
        )
    )

    action = ResearchAction(
        action=ResearchActionType.READ,
        url="https://example.com/source",
        reason="Read discovered source.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.visited_urls == ["https://example.com/source"]
    assert len(updated.read_sources) == 1
    assert updated.read_count == 1
    assert updated.steps == 1
    assert updated.last_error is None


def test_repeated_read_is_blocked(
    research_state: ResearchState,
) -> None:
    research_state.search_results.append(
        SearchResult(
            title="AI Supply Chain Research",
            url="https://example.com/source",
            snippet="Relevant result.",
        )
    )
    research_state.visited_urls.append("https://example.com/source")

    action = ResearchAction(
        action=ResearchActionType.READ,
        url="https://example.com/source",
        reason="Read again.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.read_count == 0
    assert updated.last_error is not None


def test_extract_requires_read_source(
    research_state: ResearchState,
) -> None:
    evidence = make_evidence()

    action = ResearchAction(
        action=ResearchActionType.EXTRACT,
        evidence=evidence,
        reason="Extract evidence.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.evidence == []
    assert updated.last_error is not None


def test_extract_adds_evidence_from_read_source(
    research_state: ResearchState,
) -> None:
    research_state.read_sources.append(
        ReadSource(
            url="https://example.com/source",
            title="AI Supply Chain Research",
            content="AI supports planning automation.",
        )
    )

    evidence = make_evidence()

    action = ResearchAction(
        action=ResearchActionType.EXTRACT,
        evidence=evidence,
        reason="Extract evidence.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert len(updated.evidence) == 1
    assert updated.steps == 1
    assert updated.last_error is None


def test_duplicate_evidence_is_blocked(
    research_state: ResearchState,
) -> None:
    evidence = make_evidence()

    research_state.read_sources.append(
        ReadSource(
            url="https://example.com/source",
            title="AI Supply Chain Research",
            content="AI supports planning automation.",
        )
    )
    research_state.evidence.append(evidence)

    action = ResearchAction(
        action=ResearchActionType.EXTRACT,
        evidence=evidence,
        reason="Duplicate evidence.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert len(updated.evidence) == 1
    assert updated.last_error is not None


def test_finish_sufficient_with_evidence_sets_sufficient(
    research_state: ResearchState,
) -> None:
    research_state.evidence.append(make_evidence())

    action = ResearchAction(
        action=ResearchActionType.FINISH,
        finish_status=ResearchStatus.SUFFICIENT,
        reason="The objective is sufficiently supported.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.status == ResearchStatus.SUFFICIENT
    assert updated.steps == 1
    assert updated.last_error is None


def test_finish_insufficient_with_evidence_sets_insufficient(
    research_state: ResearchState,
) -> None:
    research_state.evidence.append(make_evidence())

    action = ResearchAction(
        action=ResearchActionType.FINISH,
        finish_status=ResearchStatus.INSUFFICIENT,
        reason="Evidence exists but does not sufficiently answer the objective.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.status == ResearchStatus.INSUFFICIENT
    assert updated.steps == 1
    assert len(updated.evidence) == 1
    assert updated.last_error is None


def test_finish_insufficient_without_evidence_sets_insufficient(
    research_state: ResearchState,
) -> None:
    action = ResearchAction(
        action=ResearchActionType.FINISH,
        finish_status=ResearchStatus.INSUFFICIENT,
        reason="No usable evidence found.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.status == ResearchStatus.INSUFFICIENT
    assert updated.steps == 1
    assert updated.last_error is None


def test_finish_sufficient_without_evidence_is_blocked(
    research_state: ResearchState,
) -> None:
    action = ResearchAction(
        action=ResearchActionType.FINISH,
        finish_status=ResearchStatus.SUFFICIENT,
        reason="Attempt unsupported sufficiency.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.status is None
    assert updated.steps == 0
    assert updated.last_error == (
        "FINISH cannot declare SUFFICIENT without extracted evidence."
    )


def test_finish_limit_reached_is_blocked(
    research_state: ResearchState,
) -> None:
    action = ResearchAction(
        action=ResearchActionType.FINISH,
        finish_status=ResearchStatus.LIMIT_REACHED,
        reason="Attempt to claim an operational limit semantically.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.status is None
    assert updated.steps == 0
    assert updated.last_error == (
        "FINISH cannot request LIMIT_REACHED. "
        "Operational limits are owned by the Python runtime."
    )


def test_finish_without_finish_status_is_blocked(
    research_state: ResearchState,
) -> None:
    action = ResearchAction(
        action=ResearchActionType.FINISH,
        reason="Missing semantic sufficiency judgment.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.status is None
    assert updated.steps == 0
    assert updated.last_error == (
        "FINISH requires finish_status to be SUFFICIENT or INSUFFICIENT."
    )


def test_max_steps_sets_limit_reached(
    research_state: ResearchState,
) -> None:
    research_state.steps = MAX_RESEARCH_STEPS

    action = ResearchAction(
        action=ResearchActionType.FINISH,
        reason="Attempt to continue after hard limit.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.status == ResearchStatus.LIMIT_REACHED
    assert updated.steps == MAX_RESEARCH_STEPS
    assert updated.last_error is not None


def test_max_searches_blocks_search_without_ending_research(
    research_state: ResearchState,
) -> None:
    research_state.search_count = MAX_RESEARCH_SEARCHES

    action = ResearchAction(
        action=ResearchActionType.SEARCH,
        search_query="new research query",
        reason="Attempt another search.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.status is None
    assert updated.search_count == MAX_RESEARCH_SEARCHES
    assert updated.steps == 0
    assert updated.last_error == (
        "Maximum research searches reached. Choose another valid action."
    )


def test_search_limit_allows_recovery_with_read(
    research_state: ResearchState,
) -> None:
    research_state.search_results.append(
        SearchResult(
            title="AI Supply Chain Research",
            url="https://example.com/source",
            snippet="Relevant result.",
        )
    )
    research_state.search_count = MAX_RESEARCH_SEARCHES

    blocked_search = ResearchAction(
        action=ResearchActionType.SEARCH,
        search_query="another research query",
        reason="Attempt another search.",
    )

    after_block = execute_research_action(
        state=research_state,
        action=blocked_search,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert after_block.status is None
    assert after_block.steps == 0
    assert after_block.last_error is not None

    recovery_read = ResearchAction(
        action=ResearchActionType.READ,
        url="https://example.com/source",
        reason="Use an already discovered source instead.",
    )

    recovered = execute_research_action(
        state=after_block,
        action=recovery_read,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert recovered.status is None
    assert recovered.read_count == 1
    assert recovered.steps == 1
    assert recovered.visited_urls == ["https://example.com/source"]
    assert recovered.last_error is None


def test_max_reads_blocks_read_without_ending_research(
    research_state: ResearchState,
) -> None:
    research_state.search_results.append(
        SearchResult(
            title="AI Supply Chain Research",
            url="https://example.com/source",
            snippet="Relevant result.",
        )
    )
    research_state.read_count = MAX_RESEARCH_READS

    action = ResearchAction(
        action=ResearchActionType.READ,
        url="https://example.com/source",
        reason="Attempt another read.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.status is None
    assert updated.read_count == MAX_RESEARCH_READS
    assert updated.steps == 0
    assert updated.last_error == (
        "Maximum research reads reached. Choose another valid action."
    )


def test_max_evidence_items_blocks_extract_without_ending_research(
    research_state: ResearchState,
) -> None:
    research_state.read_sources.append(
        ReadSource(
            url="https://example.com/source",
            title="AI Supply Chain Research",
            content="AI supports planning automation.",
        )
    )

    for index in range(MAX_RESEARCH_EVIDENCE_ITEMS):
        research_state.evidence.append(make_evidence(index))

    new_evidence = make_evidence(MAX_RESEARCH_EVIDENCE_ITEMS)

    action = ResearchAction(
        action=ResearchActionType.EXTRACT,
        evidence=new_evidence,
        reason="Attempt another extraction.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.status is None
    assert len(updated.evidence) == MAX_RESEARCH_EVIDENCE_ITEMS
    assert updated.steps == 0
    assert updated.last_error == (
        "Maximum research evidence items reached. Choose another valid action."
    )


def test_search_without_query_is_blocked(
    research_state: ResearchState,
) -> None:
    action = ResearchAction(
        action=ResearchActionType.SEARCH,
        reason="Search without a query.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.search_count == 0
    assert updated.steps == 0
    assert updated.last_error is not None


def test_read_without_url_is_blocked(
    research_state: ResearchState,
) -> None:
    action = ResearchAction(
        action=ResearchActionType.READ,
        reason="Read without a URL.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.read_count == 0
    assert updated.steps == 0
    assert updated.last_error is not None


def test_extract_without_evidence_is_blocked(
    research_state: ResearchState,
) -> None:
    action = ResearchAction(
        action=ResearchActionType.EXTRACT,
        reason="Extract without evidence.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.evidence == []
    assert updated.steps == 0
    assert updated.last_error is not None


def test_extract_with_mismatched_source_title_is_blocked(
    research_state: ResearchState,
) -> None:
    research_state.read_sources.append(
        ReadSource(
            url="https://example.com/source",
            title="AI Supply Chain Research",
            content="AI supports planning automation.",
        )
    )

    evidence = make_evidence(source_title="Invented Source Title")

    action = ResearchAction(
        action=ResearchActionType.EXTRACT,
        evidence=evidence,
        reason="Extract evidence with mismatched source metadata.",
    )

    updated = execute_research_action(
        state=research_state,
        action=action,
        search_tool=fake_search,
        read_tool=fake_reader,
    )

    assert updated.evidence == []
    assert updated.steps == 0
    assert updated.last_error is not None
    