from time import perf_counter

from openai import OpenAI

from app.config.settings import MODEL_NAME, OPENAI_API_KEY
from app.prompts.argument_intelligence import ARGUMENT_INTELLIGENCE_SYSTEM_PROMPT
from app.schemas.argument import ArgumentBrief, ArgumentSynthesis
from app.schemas.research import EvidenceItem, ResearchBrief
from app.telemetry.usage import record_openai_usage


client = OpenAI(api_key=OPENAI_API_KEY)


def build_argument_brief(
    research_brief: ResearchBrief,
    synthesis: ArgumentSynthesis,
) -> ArgumentBrief:
    """
    Build a validated ArgumentBrief from an LLM-owned ArgumentSynthesis.

    The LLM may select evidence by index, but it does not recreate or mutate
    EvidenceItem objects. Evidence provenance remains owned by the upstream
    ResearchBrief and is resolved deterministically by the Python runtime.
    """

    strongest_evidence = _resolve_evidence_indices(
        evidence=research_brief.evidence,
        indices=synthesis.strongest_evidence_indices,
        field_name="strongest_evidence_indices",
    )

    strongest_counterevidence = _resolve_evidence_indices(
        evidence=research_brief.evidence,
        indices=synthesis.strongest_counterevidence_indices,
        field_name="strongest_counterevidence_indices",
    )

    return ArgumentBrief(
        original_thesis=synthesis.original_thesis,
        relevant_context=synthesis.relevant_context,
        strongest_evidence=strongest_evidence,
        strongest_counterevidence=strongest_counterevidence,
        central_tensions=synthesis.central_tensions,
        uncertainties=synthesis.uncertainties,
        contribution_areas=synthesis.contribution_areas,
    )


def generate_argument_brief(
    research_brief: ResearchBrief,
) -> ArgumentBrief:
    """
    Generate an ArgumentBrief from a completed ResearchBrief.

    The LLM performs semantic synthesis only. The Python runtime resolves
    evidence references against the original ResearchBrief before constructing
    the final ArgumentBrief.
    """

    user_content = _build_argument_input(research_brief)

    started_at = perf_counter()
    response = client.responses.parse(
        model=MODEL_NAME,
        instructions=ARGUMENT_INTELLIGENCE_SYSTEM_PROMPT,
        input=user_content,
        text_format=ArgumentSynthesis,
    )

    record_openai_usage(
        component="argument_intelligence",
        operation="generate_argument_brief",
        model=MODEL_NAME,
        response=response,
        latency_ms=(perf_counter() - started_at) * 1000,
    )

    synthesis = response.output_parsed

    if synthesis is None:
        raise RuntimeError(
            "Argument Intelligence returned no structured synthesis."
        )

    return build_argument_brief(
        research_brief=research_brief,
        synthesis=synthesis,
    )


def _build_argument_input(
    research_brief: ResearchBrief,
) -> str:
    """
    Build the bounded semantic input supplied to Argument Intelligence.

    Evidence indices are made explicit so the LLM can reference existing
    EvidenceItem objects without recreating them.
    """

    indexed_evidence = (
        "\n\n".join(
            (
                f"EVIDENCE INDEX: {index}\n"
                f"{evidence.model_dump_json(indent=2)}"
            )
            for index, evidence in enumerate(research_brief.evidence)
        )
        if research_brief.evidence
        else "None"
    )

    return f"""
RESEARCH OBJECTIVE:
{research_brief.research_objective.model_dump_json(indent=2)}

RESEARCH STATUS:
{research_brief.status.value}

RESEARCH SUMMARY:
{research_brief.summary}

KEY FINDINGS:
{research_brief.key_findings}

EXTRACTED EVIDENCE:
{indexed_evidence}

COUNTERPOINTS:
{research_brief.counterpoints}

UNRESOLVED QUESTIONS:
{research_brief.unresolved_questions}
""".strip()


def _resolve_evidence_indices(
    evidence: list[EvidenceItem],
    indices: list[int],
    field_name: str,
) -> list[EvidenceItem]:
    """
    Resolve zero-based evidence indices against the original ResearchBrief.

    Invalid or duplicate indices are rejected rather than silently corrected.
    """

    if len(indices) != len(set(indices)):
        raise ValueError(
            f"{field_name} contains duplicate evidence indices."
        )

    resolved: list[EvidenceItem] = []

    for index in indices:
        if index < 0 or index >= len(evidence):
            raise ValueError(
                f"{field_name} contains invalid evidence index {index}. "
                f"ResearchBrief contains {len(evidence)} evidence item(s)."
            )

        resolved.append(evidence[index])

    return resolved