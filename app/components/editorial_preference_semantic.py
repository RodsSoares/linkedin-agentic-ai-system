from time import perf_counter

from openai import OpenAI

from app.config.settings import MODEL_NAME, OPENAI_API_KEY
from app.prompts.editorial_preference import EDITORIAL_PREFERENCE_SYSTEM_PROMPT
from app.schemas.editorial_preference import (
    EditorialPreferenceEvaluation,
    EditorialPreferenceInput,
)
from app.telemetry.usage import record_openai_usage


client = OpenAI(api_key=OPENAI_API_KEY)


def evaluate_editorial_preference_semantics(
    input_data: EditorialPreferenceInput,
) -> EditorialPreferenceEvaluation:
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
CONTENT INTENT:
{input_data.content_intent}

SOURCE POST:
{input_data.source_post.post_text}

AVAILABLE RESEARCH:
{research_context}

RODRIGO VOICE CALIBRATION EVIDENCE:
{calibration_context}

DRAFT TO EVALUATE:
{input_data.draft}
""".strip()

    started_at = perf_counter()
    response = client.responses.parse(
        model=MODEL_NAME,
        instructions=EDITORIAL_PREFERENCE_SYSTEM_PROMPT,
        input=user_content,
        text_format=EditorialPreferenceEvaluation,
    )
    record_openai_usage(
        component="editorial_preference",
        operation="evaluate",
        model=MODEL_NAME,
        response=response,
        latency_ms=(perf_counter() - started_at) * 1000,
    )

    result = response.output_parsed

    if result is None:
        raise RuntimeError(
            "Editorial Preference semantic evaluation returned no structured output."
        )

    return result
