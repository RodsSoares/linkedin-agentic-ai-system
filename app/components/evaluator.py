from openai import OpenAI

from app.config.settings import MODEL_NAME, OPENAI_API_KEY
from app.prompts.evaluator import EVALUATOR_SYSTEM_PROMPT
from app.schemas.evaluator import (
    EvaluationSignals,
    EvaluatorInput,
    QualityEvaluation,
)


client = OpenAI(api_key=OPENAI_API_KEY)


MIN_FACTUAL_ACCURACY_PASS = 90
MIN_RELEVANCE_PASS = 80
MIN_VOICE_MATCH_PASS = 75

MIN_FACTUAL_ACCURACY_REJECT = 50
MIN_RELEVANCE_REJECT = 40


def calculate_voice_match(signals: EvaluationSignals) -> int:
    voice = signals.voice

    scores = [
        voice.naturalness,
        voice.directness,
        voice.practical_insight,
        voice.professional_maturity,
        voice.business_technology_fit,
        voice.anti_cliche,
        voice.non_promotional,
    ]

    return round(sum(scores) / len(scores))


def determine_decision(
    factual_accuracy: int,
    relevance: int,
    voice_match: int,
) -> str:
    if (
        factual_accuracy < MIN_FACTUAL_ACCURACY_REJECT
        or relevance < MIN_RELEVANCE_REJECT
    ):
        return "REJECT"

    if (
        factual_accuracy >= MIN_FACTUAL_ACCURACY_PASS
        and relevance >= MIN_RELEVANCE_PASS
        and voice_match >= MIN_VOICE_MATCH_PASS
    ):
        return "PASS"

    return "REVISE"


def evaluator(input_data: EvaluatorInput) -> QualityEvaluation:
    user_content = f"""
ORIGINAL POST:
{input_data.post.post_text}

DRAFT TO EVALUATE:
{input_data.current_draft}

AVAILABLE RESEARCH:
{input_data.research_result}
""".strip()

    response = client.responses.parse(
        model=MODEL_NAME,
        instructions=EVALUATOR_SYSTEM_PROMPT,
        input=user_content,
        text_format=EvaluationSignals,
    )

    signals = response.output_parsed

    if signals is None:
        raise RuntimeError("Evaluator did not return structured evaluation.")

    voice_match = calculate_voice_match(signals)

    decision = determine_decision(
        factual_accuracy=signals.factual_accuracy,
        relevance=signals.relevance,
        voice_match=voice_match,
    )

    return QualityEvaluation(
        factual_accuracy=signals.factual_accuracy,
        relevance=signals.relevance,
        voice_match=voice_match,
        decision=decision,
        revision_instruction=signals.revision_instruction,
    )