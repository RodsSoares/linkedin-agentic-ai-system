from app.components.discovery_query_builder import (
    build_discovery_queries,
)
from app.components.opportunity_evaluator import (
    evaluate_opportunity_semantics,
)
from app.components.opportunity_scoring import evaluate_opportunity
from app.components.public_discovery import run_public_discovery
from app.config.discovery_loader import load_discovery_config
from app.tools.web_tools import get_web_tools


def main() -> None:
    config = load_discovery_config()
    queries = build_discovery_queries(config)

    search_tool, read_tool = get_web_tools(mode="real")

    print("\n=== PUBLIC DISCOVERY SMOKE REAL ===")

    print("\n=== CONFIGURATION ===")
    print(
        {
            "version": config.version,
            "max_results_per_query": (
                config.search.max_results_per_query
            ),
            "max_queries": config.discovery.max_queries,
            "max_candidates": config.discovery.max_candidates,
            "max_opportunity_evaluations": (
                config.discovery.max_opportunity_evaluations
            ),
        }
    )

    print("\n=== QUERIES ===")
    for query in queries:
        print(f"- {query}")

    candidates, evaluations, measurement = run_public_discovery(
        queries=queries,
        search_tool=search_tool,
        read_tool=read_tool,
        semantic_evaluator=evaluate_opportunity_semantics,
        opportunity_scorer=evaluate_opportunity,
    )

    print("\n=== DISCOVERY MEASUREMENT ===")
    print(measurement.model_dump_json(indent=2))

    print("\n=== FUNNEL RATES ===")
    print(
        {
            "coverage_rate": measurement.coverage_rate,
            "readability_rate": measurement.readability_rate,
            "normalization_rate": measurement.normalization_rate,
            "opportunity_yield": measurement.opportunity_yield,
            "high_opportunity_yield": (
                measurement.high_opportunity_yield
            ),
        }
    )

    print("\n=== DISCOVERED OPPORTUNITIES ===")

    if not candidates:
        print("No normalized candidates found.")
        return

    ranked_results = sorted(
        zip(candidates, evaluations, strict=True),
        key=lambda item: item[1].opportunity_score,
        reverse=True,
    )

    for index, (candidate, evaluation) in enumerate(
        ranked_results,
        start=1,
    ):
        print(f"\n--- OPPORTUNITY {index} ---")
        print(f"URL: {candidate.post_url}")
        print(f"Author: {candidate.author_name}")
        print(
            "Classification: "
            f"{evaluation.classification}"
        )
        print(
            "Opportunity score: "
            f"{evaluation.opportunity_score}"
        )
        print(
            "Topic relevance: "
            f"{evaluation.topic_relevance}"
        )
        print(
            "Positioning fit: "
            f"{evaluation.positioning_fit}"
        )
        print(
            "Contribution potential: "
            f"{evaluation.contribution_potential}"
        )
        print(
            "Research cost: "
            f"{evaluation.research_cost}"
        )

        preview = " ".join(
            candidate.post_text.split()
        )[:500]

        print(f"Preview: {preview}")


if __name__ == "__main__":
    main()
    