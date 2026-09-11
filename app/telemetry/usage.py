from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Iterator


@dataclass(frozen=True)
class LLMUsageRecord:
    component: str
    operation: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cached_input_tokens: int | None = None
    reasoning_tokens: int | None = None
    latency_ms: float | None = None


@dataclass(frozen=True)
class ContextUsageRecord:
    component: str
    operation: str
    original_tokens: int
    prepared_tokens: int
    truncated: bool


@dataclass
class UsageSummary:
    llm_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cached_input_tokens: int = 0
    reasoning_tokens: int = 0
    latency_ms: float = 0.0
    context_events: int = 0
    context_original_tokens: int = 0
    context_prepared_tokens: int = 0


@dataclass
class UsageCollector:
    llm_records: list[LLMUsageRecord] = field(default_factory=list)
    context_records: list[ContextUsageRecord] = field(default_factory=list)

    def record_llm(self, record: LLMUsageRecord) -> None:
        self.llm_records.append(record)

    def record_context(self, record: ContextUsageRecord) -> None:
        self.context_records.append(record)

    def summary(self) -> UsageSummary:
        summary = UsageSummary()

        for record in self.llm_records:
            summary.llm_calls += 1
            summary.input_tokens += record.input_tokens
            summary.output_tokens += record.output_tokens
            summary.total_tokens += record.total_tokens
            summary.cached_input_tokens += record.cached_input_tokens or 0
            summary.reasoning_tokens += record.reasoning_tokens or 0
            summary.latency_ms += record.latency_ms or 0.0

        for record in self.context_records:
            summary.context_events += 1
            summary.context_original_tokens += record.original_tokens
            summary.context_prepared_tokens += record.prepared_tokens

        return summary

    def by_component(self) -> dict[str, UsageSummary]:
        components = {
            record.component
            for record in self.llm_records
        } | {
            record.component
            for record in self.context_records
        }

        result: dict[str, UsageSummary] = {}

        for component in sorted(components):
            collector = UsageCollector(
                llm_records=[
                    record
                    for record in self.llm_records
                    if record.component == component
                ],
                context_records=[
                    record
                    for record in self.context_records
                    if record.component == component
                ],
            )
            result[component] = collector.summary()

        return result


_current_collector: ContextVar[UsageCollector | None] = ContextVar(
    "token_usage_collector",
    default=None,
)


@contextmanager
def capture_usage(
    collector: UsageCollector | None = None,
) -> Iterator[UsageCollector]:
    active_collector = collector or UsageCollector()
    token = _current_collector.set(active_collector)

    try:
        yield active_collector
    finally:
        _current_collector.reset(token)


def get_current_collector() -> UsageCollector | None:
    return _current_collector.get()


def record_context_usage(
    *,
    component: str,
    operation: str,
    original_tokens: int,
    prepared_tokens: int,
    truncated: bool,
) -> None:
    collector = get_current_collector()
    if collector is None:
        return

    collector.record_context(
        ContextUsageRecord(
            component=component,
            operation=operation,
            original_tokens=original_tokens,
            prepared_tokens=prepared_tokens,
            truncated=truncated,
        )
    )


def record_openai_usage(
    *,
    component: str,
    operation: str,
    model: str,
    response: Any,
    latency_ms: float | None = None,
) -> None:
    collector = get_current_collector()
    if collector is None:
        return

    usage = getattr(response, "usage", None)
    if usage is None:
        return

    input_tokens = _coerce_non_negative_int(
        getattr(usage, "input_tokens", 0)
    )
    output_tokens = _coerce_non_negative_int(
        getattr(usage, "output_tokens", 0)
    )
    total_tokens = _coerce_non_negative_int(
        getattr(
            usage,
            "total_tokens",
            input_tokens + output_tokens,
        )
    )

    input_details = getattr(usage, "input_tokens_details", None)
    output_details = getattr(usage, "output_tokens_details", None)

    cached_input_tokens = _optional_non_negative_int(
        getattr(input_details, "cached_tokens", None)
    )
    reasoning_tokens = _optional_non_negative_int(
        getattr(output_details, "reasoning_tokens", None)
    )

    collector.record_llm(
        LLMUsageRecord(
            component=component,
            operation=operation,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cached_input_tokens=cached_input_tokens,
            reasoning_tokens=reasoning_tokens,
            latency_ms=latency_ms,
        )
    )


def _coerce_non_negative_int(value: Any) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return 0
    return max(parsed, 0)


def _optional_non_negative_int(value: Any) -> int | None:
    if value is None:
        return None
    return _coerce_non_negative_int(value)
