from app.components.discovery_query_builder import (
    build_discovery_queries,
)
from app.schemas.discovery_config import DiscoveryConfig


def _config() -> DiscoveryConfig:
    return DiscoveryConfig.model_validate(
        {
            "version": 1,
            "search": {
                "max_results_per_query": 5,
                "topics": [
                    "AI agents",
                    "AI automation",
                ],
                "strategies": [
                    {
                        "name": "linkedin_posts",
                        "enabled": True,
                        "template": (
                            'site:linkedin.com/posts/ "{topic}"'
                        ),
                    },
                    {
                        "name": "disabled_strategy",
                        "enabled": False,
                        "template": (
                            'site:example.com "{topic}"'
                        ),
                    },
                ],
            },
            "discovery": {
                "max_queries": 2,
                "max_candidates": 10,
                "max_opportunity_evaluations": 5,
            },
        }
    )


def test_builds_queries_from_enabled_strategy_and_topics():
    queries = build_discovery_queries(_config())

    assert queries == [
        'site:linkedin.com/posts/ "AI agents"',
        'site:linkedin.com/posts/ "AI automation"',
    ]


def test_disabled_strategy_is_not_used():
    queries = build_discovery_queries(_config())

    assert all(
        "example.com" not in query
        for query in queries
    )


def test_query_generation_respects_max_queries():
    config = _config()
    config.discovery.max_queries = 1

    queries = build_discovery_queries(config)

    assert queries == [
        'site:linkedin.com/posts/ "AI agents"',
    ]
    