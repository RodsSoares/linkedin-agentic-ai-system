from app.components.argument_intelligence import generate_argument_brief
from app.schemas.research import (
    EvidenceItem,
    ResearchBrief,
    ResearchObjective,
    ResearchStatus,
)


def main() -> None:
    research_brief = ResearchBrief(
        research_objective=ResearchObjective(
            question=(
                "How should organizations think about the value of AI agents "
                "in business processes?"
            ),
            focus_areas=[
                "Operational value",
                "Human decision-making",
                "Implementation constraints",
            ],
        ),
        summary=(
            "AI agents can support business processes by coordinating "
            "specialized capabilities, but realized value depends on how "
            "the technology is integrated with processes and human decisions."
        ),
        key_findings=[
            (
                "Agentic systems can coordinate multiple specialized "
                "capabilities within a workflow."
            ),
            (
                "Human oversight remains relevant when decisions involve "
                "judgment, ambiguity, or material business consequences."
            ),
            (
                "Technical capability alone does not guarantee operational "
                "value."
            ),
        ],
        evidence=[
            EvidenceItem(
                claim=(
                    "Agentic systems can coordinate specialized capabilities "
                    "within multi-step workflows."
                ),
                support=(
                    "The observed architecture separates specialized "
                    "capabilities and coordinates them through an "
                    "orchestration layer."
                ),
                source_url="https://example.com/source-1",
                source_title="Agentic Workflow Architecture",
                relevance=95,
                confidence=90,
            ),
            EvidenceItem(
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
            ),
            EvidenceItem(
                claim=(
                    "Operational value depends on process integration rather "
                    "than technical capability alone."
                ),
                support=(
                    "Deployment outcomes depend on workflow design, "
                    "governance, and integration with existing operations."
                ),
                source_url="https://example.com/source-3",
                source_title="AI and Operating Model Design",
                relevance=95,
                confidence=85,
            ),
        ],
        counterpoints=[
            (
                "Additional human checkpoints can reduce automation speed "
                "and increase operational friction."
            ),
            (
                "The appropriate degree of autonomy depends on the risk and "
                "reversibility of the decision."
            ),
        ],
        unresolved_questions=[
            (
                "How should organizations determine which decisions require "
                "mandatory human approval?"
            ),
        ],
        sources=[],
        status=ResearchStatus.SUFFICIENT,
    )

    print("\n=== ARGUMENT INTELLIGENCE REAL SMOKE ===")

    print("\n=== INPUT RESEARCH BRIEF ===")
    print(research_brief.model_dump_json(indent=2))

    argument_brief = generate_argument_brief(research_brief)

    print("\n=== ARGUMENT BRIEF ===")
    print(argument_brief.model_dump_json(indent=2))

    print("\n=== VALIDATION ===")
    print(
        {
            "original_thesis_present": bool(
                argument_brief.original_thesis.strip()
            ),
            "strongest_evidence_count": len(
                argument_brief.strongest_evidence
            ),
            "strongest_counterevidence_count": len(
                argument_brief.strongest_counterevidence
            ),
            "central_tensions_count": len(
                argument_brief.central_tensions
            ),
            "uncertainties_count": len(
                argument_brief.uncertainties
            ),
            "contribution_areas_count": len(
                argument_brief.contribution_areas
            ),
        }
    )

    selected_evidence_is_original = all(
        evidence in research_brief.evidence
        for evidence in (
            argument_brief.strongest_evidence
            + argument_brief.strongest_counterevidence
        )
    )

    print(
        "selected_evidence_is_original:",
        selected_evidence_is_original,
    )

    print("\n=== SMOKE COMPLETED ===")


if __name__ == "__main__":
    main()