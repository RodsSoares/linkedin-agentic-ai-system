from app.schemas.discovery_config import DiscoveryConfig


def build_discovery_queries(
    config: DiscoveryConfig,
) -> list[str]:
    """
    Build bounded discovery queries from enabled strategies and topics.

    Query generation is configuration-driven, while the resulting runtime
    remains bounded by discovery.max_queries.
    """

    queries: list[str] = []

    for strategy in config.search.strategies:
        if not strategy.enabled:
            continue

        for topic in config.search.topics:
            query = strategy.template.format(topic=topic).strip()

            if not query:
                continue

            queries.append(query)

            if len(queries) >= config.discovery.max_queries:
                return queries

    return queries
