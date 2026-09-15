from collections.abc import Callable

from app.components.target_qualification import qualify_target
from app.graph.nodes.opportunity_evaluator_node import (
    DEFAULT_ENGAGEMENT_POTENTIAL,
)
from app.schemas.discovery import DiscoveryMeasurement
from app.schemas.opportunity import OpportunityEvaluation, OpportunitySignals
from app.schemas.post import PostCandidate
from app.schemas.tools import ReadTool, SearchTool


OpportunitySemanticEvaluator = Callable[
    [PostCandidate],
    OpportunitySignals,
]

OpportunityScorer = Callable[
    [OpportunitySignals, int],
    OpportunityEvaluation,
]


def _normalize_candidate(
    url: str,
    content: str,
) -> PostCandidate:
    return PostCandidate(
        post_id=url,
        author_name="Unknown",
        post_text=content,
        post_url=url,
    )


def run_public_discovery(
    queries: list[str],
    search_tool: SearchTool,
    read_tool: ReadTool,
    semantic_evaluator: OpportunitySemanticEvaluator,
    opportunity_scorer: OpportunityScorer,
    known_urls: set[str] | None = None,
    engagement_potential: int = DEFAULT_ENGAGEMENT_POTENTIAL,
) -> tuple[
    list[PostCandidate],
    list[OpportunityEvaluation],
    DiscoveryMeasurement,
]:
    """
    Execute one bounded public discovery run.

    Funnel:

    search
    -> URL deduplication / novelty
    -> target qualification
    -> read
    -> PostCandidate normalization
    -> semantic opportunity evaluation
    -> deterministic opportunity scoring

    Only URLs currently classified as interaction targets are allowed to
    consume read and semantic-evaluation resources.
    """

    known = set(known_urls or set())

    discovered_urls: set[str] = set()
    novel_results: dict[str, object] = {}

    discovered_count = 0

    for query in queries:
        normalized_query = query.strip()

        if not normalized_query:
            continue

        results = search_tool(normalized_query)
        discovered_count += len(results)

        for result in results:
            url = result.url.strip()

            if not url:
                continue

            if url in discovered_urls:
                continue

            discovered_urls.add(url)

            if url in known:
                continue

            novel_results[url] = result

    qualified_urls: list[str] = []

    for url in novel_results:
        qualification = qualify_target(url)

        if qualification.is_interaction_target:
            qualified_urls.append(url)

    readable_count = 0
    candidates: list[PostCandidate] = []

    for url in qualified_urls:
        try:
            content = read_tool(url)
        except Exception:
            continue

        normalized_content = content.strip()

        if not normalized_content:
            continue

        readable_count += 1

        try:
            candidate = _normalize_candidate(
                url=url,
                content=normalized_content,
            )
        except Exception:
            continue

        candidates.append(candidate)

    evaluations: list[OpportunityEvaluation] = []

    high_count = 0
    medium_count = 0
    low_count = 0

    for candidate in candidates:
        signals = semantic_evaluator(candidate)

        evaluation = opportunity_scorer(
            signals,
            engagement_potential,
        )

        evaluations.append(evaluation)

        if evaluation.classification == "HIGH":
            high_count += 1
        elif evaluation.classification == "MEDIUM":
            medium_count += 1
        elif evaluation.classification == "LOW":
            low_count += 1
        else:
            raise ValueError(
                "Unsupported opportunity classification: "
                f"{evaluation.classification}"
            )

    measurement = DiscoveryMeasurement(
        query_count=len(
            [
                query
                for query in queries
                if query.strip()
            ]
        ),
        discovered_count=discovered_count,
        novel_count=len(novel_results),
        readable_count=readable_count,
        normalized_count=len(candidates),
        opportunity_evaluated_count=len(evaluations),
        high_opportunity_count=high_count,
        medium_opportunity_count=medium_count,
        low_opportunity_count=low_count,
    )

    return candidates, evaluations, measurement
