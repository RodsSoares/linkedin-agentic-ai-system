from time import perf_counter

from openai import OpenAI

from app.config.settings import MODEL_NAME, OPENAI_API_KEY
from app.prompts.perspective_generation import (
    PERSPECTIVE_GENERATION_SYSTEM_PROMPT,
)
from app.schemas.argument import (
    ArgumentBrief,
    Perspective,
    PerspectiveSet,
    PerspectiveSetSynthesis,
    PerspectiveSynthesis,
)
from app.schemas.research import EvidenceItem
from app.telemetry.usage import record_openai_usage


client = OpenAI(api_key=OPENAI_API_KEY)


def build_perspective_set(
    argument_brief: ArgumentBrief,
    synthesis: PerspectiveSetSynthesis,
) -> PerspectiveSet:
    """
    Convert LLM-owned perspective synthesis into the runtime PerspectiveSet.

    Evidence references are resolved deterministically against a unique
    evidence pool derived from the ArgumentBrief.
    """

    evidence_pool = _build_evidence_pool(argument_brief)

    perspectives = [
        _build_perspective(
            perspective_synthesis=perspective_synthesis,
            evidence_pool=evidence_pool,
        )
        for perspective_synthesis in synthesis.perspectives
    ]

    _validate_unique_perspective_ids(perspectives)

    return PerspectiveSet(perspectives=perspectives)


def generate_perspective_set(
    argument_brief: ArgumentBrief,
) -> PerspectiveSet:
    """
    Generate candidate intellectual perspectives from an ArgumentBrief.

    The LLM owns semantic divergence.
    Python owns structural validation and evidence provenance.
    """

    user_content = _build_perspective_input(argument_brief)

    started_at = perf_counter()

    response = client.responses.parse(
        model=MODEL_NAME,
        instructions=PERSPECTIVE_GENERATION_SYSTEM_PROMPT,
        input=user_content,
        text_format=PerspectiveSetSynthesis,
    )

    record_openai_usage(
        component="perspective_generation",
        operation="generate_perspective_set",
        model=MODEL_NAME,
        response=response,
        latency_ms=(perf_counter() - started_at) * 1000,
    )

    synthesis = response.output_parsed

    if synthesis is None:
        raise RuntimeError(
            "Perspective Generation returned no structured synthesis."
        )

    return build_perspective_set(
        argument_brief=argument_brief,
        synthesis=synthesis,
    )


def _build_perspective_input(
    argument_brief: ArgumentBrief,
) -> str:
    evidence_pool = _build_evidence_pool(argument_brief)

    indexed_evidence = (
        "\n\n".join(
            (
                f"EVIDENCE INDEX: {index}\n"
                f"{evidence.model_dump_json(indent=2)}"
            )
            for index, evidence in enumerate(evidence_pool)
        )
        if evidence_pool
        else "None"
    )

    return f"""
ORIGINAL THESIS:
{argument_brief.original_thesis}

RELEVANT CONTEXT:
{argument_brief.relevant_context}

EVIDENCE POOL:
{indexed_evidence}

CENTRAL TENSIONS:
{argument_brief.central_tensions}

UNCERTAINTIES:
{argument_brief.uncertainties}

CONTRIBUTION AREAS:
{argument_brief.contribution_areas}
""".strip()


def _build_perspective(
    perspective_synthesis: PerspectiveSynthesis,
    evidence_pool: list[EvidenceItem],
) -> Perspective:
    supporting_evidence = _resolve_evidence_indices(
        evidence=evidence_pool,
        indices=perspective_synthesis.supporting_evidence_indices,
        field_name="supporting_evidence_indices",
    )

    return Perspective(
        perspective_id=perspective_synthesis.perspective_id,
        label=perspective_synthesis.label,
        core_argument=perspective_synthesis.core_argument,
        why_it_matters=perspective_synthesis.why_it_matters,
        supporting_evidence=supporting_evidence,
        counterargument=perspective_synthesis.counterargument,
        uncertainty=perspective_synthesis.uncertainty,
        contribution=perspective_synthesis.contribution,
    )


def _build_evidence_pool(
    argument_brief: ArgumentBrief,
) -> list[EvidenceItem]:
    """
    Build one deterministic evidence pool from supporting and counterevidence.

    Duplicate EvidenceItem objects are included only once while preserving
    first-seen order.
    """

    evidence_pool: list[EvidenceItem] = []

    for evidence in (
        argument_brief.strongest_evidence
        + argument_brief.strongest_counterevidence
    ):
        if evidence not in evidence_pool:
            evidence_pool.append(evidence)

    return evidence_pool


def _resolve_evidence_indices(
    evidence: list[EvidenceItem],
    indices: list[int],
    field_name: str,
) -> list[EvidenceItem]:
    if len(indices) != len(set(indices)):
        raise ValueError(
            f"{field_name} contains duplicate evidence indices."
        )

    resolved: list[EvidenceItem] = []

    for index in indices:
        if index < 0 or index >= len(evidence):
            raise ValueError(
                f"{field_name} contains invalid evidence index: {index}."
            )

        resolved.append(evidence[index])

    return resolved


def _validate_unique_perspective_ids(
    perspectives: list[Perspective],
) -> None:
    perspective_ids = [
        perspective.perspective_id
        for perspective in perspectives
    ]

    if len(perspective_ids) != len(set(perspective_ids)):
        raise ValueError(
            "PerspectiveSet contains duplicate perspective_id values."
        )