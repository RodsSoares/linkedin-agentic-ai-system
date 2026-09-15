import json

import pytest

from app.config.discovery_loader import (
    DiscoveryConfigError,
    load_discovery_config,
)
from app.schemas.discovery_config import DiscoveryConfig


def _valid_config() -> dict:
    return {
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
                }
            ],
        },
        "discovery": {
            "max_queries": 2,
            "max_candidates": 10,
            "max_opportunity_evaluations": 5,
        },
    }


def test_valid_discovery_config_is_accepted():
    config = DiscoveryConfig.model_validate(_valid_config())

    assert config.version == 1
    assert config.search.max_results_per_query == 5
    assert config.search.topics == [
        "AI agents",
        "AI automation",
    ]
    assert config.search.strategies[0].name == "linkedin_posts"
    assert config.search.strategies[0].enabled is True
    assert config.discovery.max_queries == 2


def test_topic_whitespace_is_normalized():
    raw_config = _valid_config()
    raw_config["search"]["topics"] = [
        "  AI agents  ",
        "Supply Chain AI",
    ]

    config = DiscoveryConfig.model_validate(raw_config)

    assert config.search.topics == [
        "AI agents",
        "Supply Chain AI",
    ]


def test_blank_topic_is_rejected():
    raw_config = _valid_config()
    raw_config["search"]["topics"] = [
        "AI agents",
        "   ",
    ]

    with pytest.raises(ValueError):
        DiscoveryConfig.model_validate(raw_config)


def test_duplicate_topics_are_rejected_case_insensitively():
    raw_config = _valid_config()
    raw_config["search"]["topics"] = [
        "AI agents",
        "ai AGENTS",
    ]

    with pytest.raises(ValueError):
        DiscoveryConfig.model_validate(raw_config)


def test_strategy_template_requires_topic_placeholder():
    raw_config = _valid_config()
    raw_config["search"]["strategies"][0]["template"] = (
        "site:linkedin.com/posts/ AI agents"
    )

    with pytest.raises(ValueError):
        DiscoveryConfig.model_validate(raw_config)


def test_at_least_one_strategy_must_be_enabled():
    raw_config = _valid_config()
    raw_config["search"]["strategies"][0]["enabled"] = False

    with pytest.raises(ValueError):
        DiscoveryConfig.model_validate(raw_config)


def test_strategy_names_must_be_unique():
    raw_config = _valid_config()
    raw_config["search"]["strategies"].append(
        {
            "name": "LINKEDIN_POSTS",
            "enabled": True,
            "template": (
                'site:linkedin.com/feed/update/ "{topic}"'
            ),
        }
    )

    with pytest.raises(ValueError):
        DiscoveryConfig.model_validate(raw_config)


def test_max_queries_cannot_exceed_available_queries():
    raw_config = _valid_config()
    raw_config["discovery"]["max_queries"] = 3

    with pytest.raises(ValueError):
        DiscoveryConfig.model_validate(raw_config)


def test_loader_reads_valid_json_file(tmp_path):
    config_path = tmp_path / "discovery.json"
    config_path.write_text(
        json.dumps(_valid_config()),
        encoding="utf-8",
    )

    config = load_discovery_config(config_path)

    assert isinstance(config, DiscoveryConfig)
    assert config.search.topics[0] == "AI agents"


def test_loader_rejects_missing_file(tmp_path):
    missing_path = tmp_path / "missing.json"

    with pytest.raises(
        DiscoveryConfigError,
        match="not found",
    ):
        load_discovery_config(missing_path)


def test_loader_rejects_invalid_json(tmp_path):
    config_path = tmp_path / "discovery.json"
    config_path.write_text(
        "{invalid-json",
        encoding="utf-8",
    )

    with pytest.raises(
        DiscoveryConfigError,
        match="Invalid JSON",
    ):
        load_discovery_config(config_path)


def test_loader_rejects_schema_invalid_configuration(tmp_path):
    raw_config = _valid_config()
    raw_config["search"]["max_results_per_query"] = 0

    config_path = tmp_path / "discovery.json"
    config_path.write_text(
        json.dumps(raw_config),
        encoding="utf-8",
    )

    with pytest.raises(
        DiscoveryConfigError,
        match="Invalid discovery configuration",
    ):
        load_discovery_config(config_path)


def test_default_repository_configuration_loads():
    config = load_discovery_config()

    assert config.version == 1
    assert config.search.topics
    assert any(
        strategy.enabled
        for strategy in config.search.strategies
    )
    