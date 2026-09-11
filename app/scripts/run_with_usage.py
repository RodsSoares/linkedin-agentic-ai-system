from __future__ import annotations

import os
import time
from typing import Any

# Controlled live E2E diagnostic runner.
# Select real web mode before importing application modules.
os.environ["WEB_TOOL_MODE"] = "real"

from app.graph.workflow import build_scout_opportunity_workflow
from app.telemetry.usage import UsageCollector, capture_usage


SCOUT_OBJECTIVE = """
Find a current public web article, discussion, or professional publication
where Rodrigo can make a relevant and differentiated contribution about
AI agents, intelligent automation, AI applied to business processes,
supply chain, operations, or AI solution architecture.

Prefer recent, substantive content where a practical business and
engineering perspective would add value.

Select exactly one strong candidate when appropriate. Do not force a
selection if no candidate is good enough.
""".strip()


def _serialize(value: Any) -> Any:
    if value is None:
        return None

    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")

    if hasattr(value, "value"):
        return value.value

    return value


def _print_section(title: str, value: Any) -> None:
    print(f"\n=== {title} ===")

    serialized = _serialize(value)

    if isinstance(serialized, dict):
        for key, item in serialized.items():
            print(f"{key}: {_serialize(item)}")
        return

    print(serialized)


def _print_usage_report(
    usage: UsageCollector,
    *,
    workflow_elapsed_seconds: float,
) -> None:
    summary = usage.summary()
    by_component = usage.by_component()

    print("\n=== TOKEN USAGE BY COMPONENT ===")
    print(
        f"{'component':<16}"
        f"{'calls':>7}"
        f"{'input':>11}"
        f"{'output':>11}"
        f"{'total':>11}"
        f"{'cached':>11}"
        f"{'reasoning':>12}"
        f"{'llm_s':>11}"
    )
    print("-" * 90)

    for component, component_summary in by_component.items():
        print(
            f"{component:<16}"
            f"{component_summary.llm_calls:>7}"
            f"{component_summary.input_tokens:>11}"
            f"{component_summary.output_tokens:>11}"
            f"{component_summary.total_tokens:>11}"
            f"{component_summary.cached_input_tokens:>11}"
            f"{component_summary.reasoning_tokens:>12}"
            f"{component_summary.latency_ms / 1000:>11.2f}"
        )

    print("-" * 90)
    print(
        f"{'TOTAL':<16}"
        f"{summary.llm_calls:>7}"
        f"{summary.input_tokens:>11}"
        f"{summary.output_tokens:>11}"
        f"{summary.total_tokens:>11}"
        f"{summary.cached_input_tokens:>11}"
        f"{summary.reasoning_tokens:>12}"
        f"{summary.latency_ms / 1000:>11.2f}"
    )

    print("\n=== LLM CALLS BY OPERATION ===")

    if not usage.llm_records:
        print("No LLM usage records were captured.")
    else:
        for index, record in enumerate(usage.llm_records, start=1):
            print(
                f"{index:>2}. "
                f"{record.component}.{record.operation} | "
                f"model={record.model} | "
                f"in={record.input_tokens} | "
                f"out={record.output_tokens} | "
                f"total={record.total_tokens} | "
                f"cached={record.cached_input_tokens or 0} | "
                f"reasoning={record.reasoning_tokens or 0} | "
                f"latency={((record.latency_ms or 0.0) / 1000):.2f}s"
            )

    print("\n=== PREPARED CONTEXT EVENTS ===")
    print(
        f"{'component':<16}"
        f"{'operation':<22}"
        f"{'original':>12}"
        f"{'prepared':>12}"
        f"{'saved':>10}"
        f"{'truncated':>12}"
    )
    print("-" * 86)

    if not usage.context_records:
        print("No prepared-context records were captured.")
    else:
        for record in usage.context_records:
            saved_tokens = max(
                record.original_tokens - record.prepared_tokens,
                0,
            )
            print(
                f"{record.component:<16}"
                f"{record.operation:<22}"
                f"{record.original_tokens:>12}"
                f"{record.prepared_tokens:>12}"
                f"{saved_tokens:>10}"
                f"{str(record.truncated):>12}"
            )

        print("-" * 86)
        saved_total = max(
            summary.context_original_tokens
            - summary.context_prepared_tokens,
            0,
        )
        print(
            f"{'TOTAL':<16}"
            f"{'':<22}"
            f"{summary.context_original_tokens:>12}"
            f"{summary.context_prepared_tokens:>12}"
            f"{saved_total:>10}"
            f"{'':>12}"
        )

    llm_seconds = summary.latency_ms / 1000
    non_llm_remainder = max(
        workflow_elapsed_seconds - llm_seconds,
        0.0,
    )

    print("\n=== LATENCY SUMMARY ===")
    print(f"workflow_elapsed_seconds: {workflow_elapsed_seconds:.2f}")
    print(f"captured_llm_seconds: {llm_seconds:.2f}")
    print(f"non_llm_remainder_seconds: {non_llm_remainder:.2f}")

    if workflow_elapsed_seconds > 0:
        llm_share = (llm_seconds / workflow_elapsed_seconds) * 100
        remainder_share = (
            non_llm_remainder / workflow_elapsed_seconds
        ) * 100

        print(f"captured_llm_share_pct: {llm_share:.1f}")
        print(f"non_llm_remainder_share_pct: {remainder_share:.1f}")

    print(
        "\nNOTE: non_llm_remainder_seconds is not a pure web-tool metric. "
        "It also includes Python/LangGraph/runtime overhead and any external "
        "work not currently instrumented."
    )


def main() -> None:
    print("=== END-TO-END TOKEN USAGE BASELINE v0.1 ===")
    print("WEB_TOOL_MODE:", os.environ["WEB_TOOL_MODE"])
    print("\n=== SCOUT OBJECTIVE ===")
    print(SCOUT_OBJECTIVE)

    workflow = build_scout_opportunity_workflow()
    result: dict[str, Any] | None = None
    failure: Exception | None = None

    started_at = time.perf_counter()

    with capture_usage() as usage:
        try:
            result = workflow.invoke(
                {
                    "scout_objective": SCOUT_OBJECTIVE,
                }
            )
        except Exception as exc:
            failure = exc

    elapsed = time.perf_counter() - started_at

    if result is not None:
        post = result.get("post")
        opportunity = result.get("opportunity_evaluation")
        research = result.get("research_result")
        draft = result.get("current_draft")
        quality = result.get("quality_evaluation")

        _print_section("POST CANDIDATE", post)
        _print_section("OPPORTUNITY EVALUATION", opportunity)
        _print_section("RESEARCH BRIEF", research)
        _print_section("FINAL DRAFT", draft)
        _print_section("QUALITY EVALUATION", quality)

        print("\n=== FINAL WORKFLOW STATE ===")
        print("status:", result.get("status"))
        print("next_step:", result.get("next_step"))
        print("iteration:", result.get("iteration"))
        print("human_feedback:", result.get("human_feedback"))

        classification = (
            getattr(opportunity, "classification", None)
            if opportunity is not None
            else None
        )
        quality_decision = (
            getattr(quality, "decision", None)
            if quality is not None
            else None
        )

        print("\n=== E2E SUMMARY ===")
        print("candidate_found:", post is not None)
        print("opportunity_classification:", classification)
        print("research_completed:", research is not None)
        print("draft_generated:", bool(draft))
        print("quality_decision:", quality_decision)

    _print_usage_report(
        usage,
        workflow_elapsed_seconds=elapsed,
    )

    if failure is not None:
        print("\n=== E2E FAILURE ===")
        print("exception_type:", type(failure).__name__)
        print("exception:", str(failure))
        print(f"elapsed_seconds: {elapsed:.2f}")
        raise failure

    print("\n=== E2E COMPLETED ===")
    print(f"elapsed_seconds: {elapsed:.2f}")


if __name__ == "__main__":
    main()
