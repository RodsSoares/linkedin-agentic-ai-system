from types import SimpleNamespace

from app.telemetry.usage import (
    UsageCollector,
    capture_usage,
    get_current_collector,
    record_context_usage,
    record_openai_usage,
)


def make_response(
    *,
    input_tokens: int = 100,
    output_tokens: int = 20,
    total_tokens: int = 120,
    cached_tokens: int | None = 10,
    reasoning_tokens: int | None = 5,
):
    return SimpleNamespace(
        usage=SimpleNamespace(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            input_tokens_details=SimpleNamespace(
                cached_tokens=cached_tokens,
            ),
            output_tokens_details=SimpleNamespace(
                reasoning_tokens=reasoning_tokens,
            ),
        )
    )


def test_usage_is_noop_without_active_collector():
    record_openai_usage(
        component="writer",
        operation="draft",
        model="test-model",
        response=make_response(),
    )

    assert get_current_collector() is None


def test_capture_usage_records_openai_usage():
    with capture_usage() as collector:
        record_openai_usage(
            component="writer",
            operation="draft",
            model="test-model",
            response=make_response(),
            latency_ms=42.5,
        )

    assert len(collector.llm_records) == 1

    record = collector.llm_records[0]
    assert record.component == "writer"
    assert record.operation == "draft"
    assert record.model == "test-model"
    assert record.input_tokens == 100
    assert record.output_tokens == 20
    assert record.total_tokens == 120
    assert record.cached_input_tokens == 10
    assert record.reasoning_tokens == 5
    assert record.latency_ms == 42.5


def test_missing_usage_is_ignored():
    with capture_usage() as collector:
        record_openai_usage(
            component="scout",
            operation="decide_next_action",
            model="test-model",
            response=SimpleNamespace(),
        )

    assert collector.llm_records == []


def test_context_usage_is_recorded():
    with capture_usage() as collector:
        record_context_usage(
            component="research",
            operation="read_context",
            original_tokens=3000,
            prepared_tokens=2500,
            truncated=True,
        )

    assert len(collector.context_records) == 1

    record = collector.context_records[0]
    assert record.component == "research"
    assert record.original_tokens == 3000
    assert record.prepared_tokens == 2500
    assert record.truncated is True


def test_summary_aggregates_llm_and_context_usage():
    with capture_usage() as collector:
        record_openai_usage(
            component="research",
            operation="decision",
            model="test-model",
            response=make_response(
                input_tokens=200,
                output_tokens=30,
                total_tokens=230,
                cached_tokens=25,
                reasoning_tokens=8,
            ),
            latency_ms=50,
        )
        record_openai_usage(
            component="research",
            operation="synthesis",
            model="test-model",
            response=make_response(
                input_tokens=300,
                output_tokens=40,
                total_tokens=340,
                cached_tokens=None,
                reasoning_tokens=None,
            ),
            latency_ms=70,
        )
        record_context_usage(
            component="research",
            operation="read_context",
            original_tokens=4000,
            prepared_tokens=2500,
            truncated=True,
        )

    summary = collector.summary()

    assert summary.llm_calls == 2
    assert summary.input_tokens == 500
    assert summary.output_tokens == 70
    assert summary.total_tokens == 570
    assert summary.cached_input_tokens == 25
    assert summary.reasoning_tokens == 8
    assert summary.latency_ms == 120
    assert summary.context_events == 1
    assert summary.context_original_tokens == 4000
    assert summary.context_prepared_tokens == 2500


def test_by_component_separates_usage():
    collector = UsageCollector()

    with capture_usage(collector):
        record_openai_usage(
            component="scout",
            operation="decision",
            model="test-model",
            response=make_response(
                input_tokens=80,
                output_tokens=10,
                total_tokens=90,
            ),
        )
        record_openai_usage(
            component="writer",
            operation="draft",
            model="test-model",
            response=make_response(
                input_tokens=120,
                output_tokens=20,
                total_tokens=140,
            ),
        )

    by_component = collector.by_component()

    assert by_component["scout"].total_tokens == 90
    assert by_component["writer"].total_tokens == 140


def test_capture_usage_restores_previous_context():
    outer = UsageCollector()

    with capture_usage(outer):
        assert get_current_collector() is outer

        with capture_usage() as inner:
            assert get_current_collector() is inner

        assert get_current_collector() is outer

    assert get_current_collector() is None
