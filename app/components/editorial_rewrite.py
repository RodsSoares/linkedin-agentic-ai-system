from time import perf_counter

from openai import OpenAI

from app.config.settings import MODEL_NAME, OPENAI_API_KEY
from app.prompts.editorial_rewrite import EDITORIAL_REWRITE_SYSTEM_PROMPT
from app.schemas.editorial_rewrite import (
    EditorialRewriteInput,
    EditorialRewriteResult,
)
from app.telemetry.usage import record_openai_usage


client = OpenAI(api_key=OPENAI_API_KEY)


def rewrite_with_editorial_preference(
    input_data: EditorialRewriteInput,
) -> EditorialRewriteResult:
    research_context = (
        input_data.research_result.model_dump_json(indent=2)
        if input_data.research_result is not None
        else "No research brief available."
    )

    calibration_context = (
        input_data.calibration_context
        if input_data.calibration_context is not None
        else "No calibration context supplied."
    )

    user_content = f"""
SOURCE POST:
{input_data.source_post.post_text}

AVAILABLE RESEARCH:
{research_context}

RODRIGO VOICE CALIBRATION EVIDENCE:
{calibration_context}

ORIGINAL DRAFT:
{input_data.original_draft}

EDITORIAL PREFERENCE EVALUATION:
{input_data.editorial_evaluation.model_dump_json(indent=2)}
""".strip()

    started_at = perf_counter()
    response = client.responses.parse(
        model=MODEL_NAME,
        instructions=EDITORIAL_REWRITE_SYSTEM_PROMPT,
        input=user_content,
        text_format=EditorialRewriteResult,
    )
    record_openai_usage(
        component="editorial_rewrite",
        operation="rewrite",
        model=MODEL_NAME,
        response=response,
        latency_ms=(perf_counter() - started_at) * 1000,
    )

    result = response.output_parsed

    if result is None:
        raise RuntimeError(
            "Editorial Rewrite returned no structured output."
        )

    return result
