from app.components.perspective_generation import generate_perspective_set
from app.schemas.argument import ArgumentBrief
from app.schemas.research import EvidenceItem


def main() -> None:
    evidence_a = EvidenceItem(
        claim=(
            "Agentic systems can coordinate specialized capabilities "
            "within multi-step workflows."
        ),
        support=(
            "The observed architecture separates specialized capabilities "
            "and coordinates them through an orchestration layer."
        ),
        source_url="https://example.com/source-1",
        source_title="Agentic Workflow Architecture",
        relevance=95,
        confidence=90,
    )

    evidence_b = EvidenceItem(
        claim=(
            "Human oversight can remain important for consequential "
            "or ambiguous decisions."
        ),
        support=(
            "Human approval provides an explicit decision boundary "
            "before consequential downstream actions."
        ),
        source_url="https://example.com/source-2",
        source_title="Human Oversight in AI Systems",
        relevance=90,
        confidence=90,
    )

    evidence_c = EvidenceItem(
        claim=(
            "Operational value depends on process integration rather "
            "than technical capability alone."
        ),
        support=(
            "Deployment outcomes depend on workflow design, governance, "
            "and integration with existing operations."
        ),
        source_url="https://example.com/source-3",
        source_title="AI and Operating Model Design",
        relevance=95,
        confidence=85,
    )

    argument_brief = ArgumentBrief(
        original_thesis=(
            "AI agents can create business-process value by coordinating "
            "specialized capabilities, but that value depends on process "
            "integration, governance, and appropriately bounded human "
            "decision-making."
        ),
        relevant_context=[
            (
                "The discussion concerns multi-step business workflows "
                "rather than isolated AI capability."
            ),
            (
                "Human involvement is most relevant where decisions are "
                "ambiguous or have consequential downstream effects."
            ),
            (
                "The degree of suitable autonomy depends on decision risk "
                "and reversibility."
            ),
        ],
        strongest_evidence=[
            evidence_a,
            evidence_b,
            evidence_c,
        ],
        strongest_counterevidence=[
            evidence_b,
            evidence_c,
        ],
        central_tensions=[
            (
                "Workflow coordination and automation speed versus human "
                "approval at consequential decision boundaries."
            ),
            (
                "Technical agent capability versus the organizational work "
                "required to redesign workflows, integrate systems, and "
                "establish governance."
            ),
            (
                "Greater autonomy versus the need to account for risk, "
                "ambiguity, and reversibility."
            ),
        ],
        uncertainties=[
            (
                "The research does not establish a specific framework or "
                "threshold for determining when human approval must be "
                "mandatory."
            ),
            (
                "The evidence does not quantify the operational value or "
                "costs of particular agent deployments."
            ),
        ],
        contribution_areas=[
            (
                "Frame AI-agent value as a workflow and operating-model "
                "outcome rather than a direct consequence of technical "
                "capability."
            ),
            (
                "Explore decision-boundary design between automated "
                "execution and explicit human approval."
            ),
            (
                "Examine risk and reversibility as practical criteria "
                "for calibrating autonomy."
            ),
            (
                "Explore how organizations can retain accountability "
                "without creating unnecessary approval friction."
            ),
        ],
    )

    print("\n=== PERSPECTIVE GENERATION REAL SMOKE ===")

    print("\n=== INPUT ARGUMENT BRIEF ===")
    print(argument_brief.model_dump_json(indent=2))

    perspective_set = generate_perspective_set(argument_brief)

    print("\n=== GENERATED PERSPECTIVES ===")

    for index, perspective in enumerate(
        perspective_set.perspectives,
        start=1,
    ):
        print(f"\n--- PERSPECTIVE {index} ---")
        print(perspective.model_dump_json(indent=2))

    print("\n=== VALIDATION ===")

    all_source_evidence = (
        argument_brief.strongest_evidence
        + argument_brief.strongest_counterevidence
    )

    selected_evidence_is_original = all(
        evidence in all_source_evidence
        for perspective in perspective_set.perspectives
        for evidence in perspective.supporting_evidence
    )

    perspective_ids = [
        perspective.perspective_id
        for perspective in perspective_set.perspectives
    ]

    print(
        {
            "perspective_count": len(
                perspective_set.perspectives
            ),
            "unique_ids": (
                len(perspective_ids)
                == len(set(perspective_ids))
            ),
            "selected_evidence_is_original": (
                selected_evidence_is_original
            ),
        }
    )

    print("\n=== SMOKE COMPLETED ===")


if __name__ == "__main__":
    main()