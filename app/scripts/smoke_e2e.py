import os
import time
from typing import Any

# This script is intentionally a controlled live smoke test.
# Set real web mode before importing application modules so the runtime
# selects Brave Search + HTTP Reader instead of deterministic fake tools.
os.environ["WEB_TOOL_MODE"] = "real"

from app.graph.workflow import build_scout_opportunity_workflow


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


def main() -> None:
    print("=== END-TO-END REAL WORKFLOW VALIDATION v0.1 ===")
    print("WEB_TOOL_MODE:", os.environ["WEB_TOOL_MODE"])
    print("\n=== SCOUT OBJECTIVE ===")
    print(SCOUT_OBJECTIVE)

    workflow = build_scout_opportunity_workflow()

    started_at = time.perf_counter()

    try:
        result = workflow.invoke(
            {
                "scout_objective": SCOUT_OBJECTIVE,
            }
        )
    except Exception as exc:
        elapsed = time.perf_counter() - started_at

        print("\n=== E2E FAILURE ===")
        print("exception_type:", type(exc).__name__)
        print("exception:", str(exc))
        print(f"elapsed_seconds: {elapsed:.2f}")
        raise

    elapsed = time.perf_counter() - started_at

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
    print(f"elapsed_seconds: {elapsed:.2f}")

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

    if post is None:
        print(
            "\nRESULT: NORMAL TERMINATION — Scout found no candidate. "
            "The mechanism completed without forcing an opportunity."
        )
    elif classification in {"LOW", "MEDIUM"}:
        print(
            f"\nRESULT: NORMAL TERMINATION — Opportunity classified as "
            f"{classification}; downstream Research/Writer execution was "
            "correctly avoided."
        )
    elif classification == "HIGH" and draft:
        print(
            "\nRESULT: HIGH OPPORTUNITY COMPLETED THROUGH THE CONTENT PATH. "
            "Review the draft and Quality Evaluation above before any manual "
            "publication."
        )
    else:
        print(
            "\nRESULT: Workflow terminated, but the resulting state should be "
            "reviewed because it does not match one of the expected smoke-test "
            "terminal patterns."
        )


if __name__ == "__main__":
    main()
    