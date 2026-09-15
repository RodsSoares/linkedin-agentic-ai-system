from app.components.opportunity_scoring import evaluate_opportunity
from app.components.public_discovery import run_public_discovery
from app.schemas.opportunity import OpportunitySignals
from app.schemas.post import PostCandidate
from app.schemas.tools import SearchResult


POST_1 = (
    "https://www.linkedin.com/posts/"
    "example-ai-agents-activity-1001"
)

POST_2 = (
    "https://www.linkedin.com/posts/"
    "example-supply-chain-ai-activity-1002"
)

POST_3 = (
    "https://www.linkedin.com/posts/"
    "example-business-ai-activity-1003"
)

KNOWN_POST = (
    "https://www.linkedin.com/posts/"
    "example-known-activity-1004"
)

COMPANY_PAGE = "https://www.linkedin.com/company/example-ai"

EXTERNAL_PAGE = "https://www.coursera.org/learn/ai"


def _search_tool(query: str) -> list[SearchResult]:
    results_by_query = {
        "ai agents": [
            SearchResult(
                title="AI agents in operations",
                url=POST_1,
                snippet="AI agents and operations.",
            ),
            SearchResult(
                title="Supply chain automation",
                url=POST_2,
                snippet="Automation in supply chain.",
            ),
            SearchResult(
                title="Company page",
                url=COMPANY_PAGE,
                snippet="LinkedIn company page.",
            ),
        ],
        "supply chain ai": [
            SearchResult(
                title="Supply chain automation duplicate",
                url=POST_2,
                snippet="Duplicate result.",
            ),
            SearchResult(
                title="Business AI",
                url=POST_3,
                snippet="AI transformation.",
            ),
            SearchResult(
                title="Known post",
                url=KNOWN_POST,
                snippet="Already known.",
            ),
            SearchResult(
                title="External course",
                url=EXTERNAL_PAGE,
                snippet="External content.",
            ),
        ],
    }

    return results_by_query.get(query, [])


def _read_tool(url: str) -> str:
    content_by_url = {
        POST_1: (
            "AI agents are changing operational decision making."
        ),
        POST_2: (
            "Supply chain teams are adopting AI automation."
        ),
        POST_3: "",
    }

    return content_by_url[url]


def _semantic_evaluator(
    post: PostCandidate,
) -> OpportunitySignals:
    signals_by_url = {
        POST_1: OpportunitySignals(
            topic_relevance=95,
            positioning_fit=90,
            contribution_potential=90,
            research_cost=20,
        ),
        POST_2: OpportunitySignals(
            topic_relevance=70,
            positioning_fit=70,
            contribution_potential=70,
            research_cost=40,
        ),
    }

    return signals_by_url[post.post_url]


def test_public_discovery_runs_qualified_funnel() -> None:
    candidates, evaluations, measurement = run_public_discovery(
        queries=[
            "ai agents",
            "supply chain ai",
        ],
        search_tool=_search_tool,
        read_tool=_read_tool,
        semantic_evaluator=_semantic_evaluator,
        opportunity_scorer=evaluate_opportunity,
        known_urls={KNOWN_POST},
    )

    assert len(candidates) == 2
    assert len(evaluations) == 2

    assert {
        candidate.post_url
        for candidate in candidates
    } == {
        POST_1,
        POST_2,
    }

    assert measurement.query_count == 2

    # Seven raw search-result appearances.
    assert measurement.discovered_count == 7

    # Six unique URLs survive duplicate/known filtering:
    # POST_1, POST_2, company, POST_3, external.
    # KNOWN_POST is excluded, and POST_2 appears twice.
    assert measurement.novel_count == 5

    # Only POST_1, POST_2 and POST_3 qualify as interaction targets.
    # POST_3 returns empty content.
    assert measurement.readable_count == 2
    assert measurement.normalized_count == 2
    assert measurement.opportunity_evaluated_count == 2

    assert measurement.high_opportunity_count == 1
    assert measurement.medium_opportunity_count == 1
    assert measurement.low_opportunity_count == 0


def test_non_interaction_targets_are_not_read() -> None:
    read_urls: list[str] = []

    def tracking_reader(url: str) -> str:
        read_urls.append(url)
        return _read_tool(url)

    run_public_discovery(
        queries=[
            "ai agents",
            "supply chain ai",
        ],
        search_tool=_search_tool,
        read_tool=tracking_reader,
        semantic_evaluator=_semantic_evaluator,
        opportunity_scorer=evaluate_opportunity,
        known_urls={KNOWN_POST},
    )

    assert COMPANY_PAGE not in read_urls
    assert EXTERNAL_PAGE not in read_urls

    assert POST_1 in read_urls
    assert POST_2 in read_urls
    assert POST_3 in read_urls


def test_known_urls_are_excluded_before_reading() -> None:
    read_urls: list[str] = []

    def tracking_reader(url: str) -> str:
        read_urls.append(url)
        return _read_tool(url)

    run_public_discovery(
        queries=["supply chain ai"],
        search_tool=_search_tool,
        read_tool=tracking_reader,
        semantic_evaluator=_semantic_evaluator,
        opportunity_scorer=evaluate_opportunity,
        known_urls={KNOWN_POST},
    )

    assert KNOWN_POST not in read_urls


def test_duplicate_urls_are_read_only_once() -> None:
    read_urls: list[str] = []

    def tracking_reader(url: str) -> str:
        read_urls.append(url)
        return _read_tool(url)

    run_public_discovery(
        queries=[
            "ai agents",
            "supply chain ai",
        ],
        search_tool=_search_tool,
        read_tool=tracking_reader,
        semantic_evaluator=_semantic_evaluator,
        opportunity_scorer=evaluate_opportunity,
        known_urls={KNOWN_POST},
    )

    assert read_urls.count(POST_2) == 1


def test_blank_queries_do_not_execute_search() -> None:
    search_queries: list[str] = []

    def tracking_search(query: str) -> list[SearchResult]:
        search_queries.append(query)
        return []

    candidates, evaluations, measurement = run_public_discovery(
        queries=["", "   "],
        search_tool=tracking_search,
        read_tool=_read_tool,
        semantic_evaluator=_semantic_evaluator,
        opportunity_scorer=evaluate_opportunity,
    )

    assert search_queries == []
    assert candidates == []
    assert evaluations == []
    assert measurement.query_count == 0


def test_semantic_failure_is_not_converted_to_low() -> None:
    def failing_semantic_evaluator(
        post: PostCandidate,
    ) -> OpportunitySignals:
        raise RuntimeError("semantic evaluation failed")

    try:
        run_public_discovery(
            queries=["ai agents"],
            search_tool=_search_tool,
            read_tool=_read_tool,
            semantic_evaluator=failing_semantic_evaluator,
            opportunity_scorer=evaluate_opportunity,
        )
    except RuntimeError as exc:
        assert str(exc) == "semantic evaluation failed"
    else:
        raise AssertionError(
            "Semantic evaluation failure should propagate."
        )
    