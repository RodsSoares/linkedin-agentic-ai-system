import pytest
from pydantic import ValidationError

from app.schemas.discovery import DiscoveryMeasurement


def test_discovery_measurement_accepts_valid_funnel() -> None:
    measurement = DiscoveryMeasurement(
        query_count=5,
        discovered_count=25,
        novel_count=17,
        readable_count=11,
        normalized_count=9,
        opportunity_evaluated_count=9,
        high_opportunity_count=3,
        medium_opportunity_count=4,
        low_opportunity_count=2,
    )

    assert measurement.query_count == 5
    assert measurement.discovered_count == 25
    assert measurement.novel_count == 17
    assert measurement.readable_count == 11
    assert measurement.normalized_count == 9

    assert measurement.duplicate_or_known_count == 8
    assert measurement.unreadable_count == 6
    assert measurement.normalization_failure_count == 2

    assert measurement.coverage_rate == 0.68
    assert measurement.readability_rate == 0.6471
    assert measurement.normalization_rate == 0.8182
    assert measurement.opportunity_yield == 0.7778
    assert measurement.high_opportunity_yield == 0.3333


def test_discovery_measurement_returns_zero_rates_for_empty_run() -> None:
    measurement = DiscoveryMeasurement()

    assert measurement.coverage_rate == 0.0
    assert measurement.readability_rate == 0.0
    assert measurement.normalization_rate == 0.0
    assert measurement.opportunity_yield == 0.0
    assert measurement.high_opportunity_yield == 0.0


def test_discovery_measurement_rejects_novel_count_above_discovered() -> None:
    with pytest.raises(
        ValidationError,
        match="novel_count cannot exceed discovered_count",
    ):
        DiscoveryMeasurement(
            discovered_count=5,
            novel_count=6,
        )


def test_discovery_measurement_rejects_readable_count_above_novel() -> None:
    with pytest.raises(
        ValidationError,
        match="readable_count cannot exceed novel_count",
    ):
        DiscoveryMeasurement(
            discovered_count=10,
            novel_count=5,
            readable_count=6,
        )


def test_discovery_measurement_rejects_normalized_count_above_readable() -> None:
    with pytest.raises(
        ValidationError,
        match="normalized_count cannot exceed readable_count",
    ):
        DiscoveryMeasurement(
            discovered_count=10,
            novel_count=8,
            readable_count=5,
            normalized_count=6,
        )


def test_discovery_measurement_rejects_evaluated_count_above_normalized() -> None:
    with pytest.raises(
        ValidationError,
        match=(
            "opportunity_evaluated_count cannot exceed normalized_count"
        ),
    ):
        DiscoveryMeasurement(
            discovered_count=10,
            novel_count=8,
            readable_count=7,
            normalized_count=5,
            opportunity_evaluated_count=6,
            high_opportunity_count=2,
            medium_opportunity_count=2,
            low_opportunity_count=2,
        )


def test_discovery_measurement_requires_classification_total_to_match_evaluated() -> None:
    with pytest.raises(
        ValidationError,
        match=(
            "HIGH \\+ MEDIUM \\+ LOW opportunity counts must equal "
            "opportunity_evaluated_count"
        ),
    ):
        DiscoveryMeasurement(
            discovered_count=10,
            novel_count=8,
            readable_count=7,
            normalized_count=6,
            opportunity_evaluated_count=6,
            high_opportunity_count=2,
            medium_opportunity_count=2,
            low_opportunity_count=1,
        )


def test_low_opportunities_do_not_count_as_opportunity_yield() -> None:
    measurement = DiscoveryMeasurement(
        discovered_count=10,
        novel_count=10,
        readable_count=10,
        normalized_count=10,
        opportunity_evaluated_count=10,
        high_opportunity_count=1,
        medium_opportunity_count=2,
        low_opportunity_count=7,
    )

    assert measurement.opportunity_yield == 0.3
    assert measurement.high_opportunity_yield == 0.1
    