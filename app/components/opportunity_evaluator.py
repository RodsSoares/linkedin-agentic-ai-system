from openai import OpenAI

from app.config.settings import MODEL_NAME, OPENAI_API_KEY
from app.prompts.opportunity import OPPORTUNITY_SYSTEM_PROMPT
from app.schemas.opportunity import OpportunitySignals
from app.schemas.post import PostCandidate


client = OpenAI(api_key=OPENAI_API_KEY)


def evaluate_opportunity_semantics(post: PostCandidate) -> OpportunitySignals:
    user_content = f"""
POST AUTHOR:
{post.author_name}

POST:
{post.post_text}
""".strip()

    response = client.responses.parse(
        model=MODEL_NAME,
        instructions=OPPORTUNITY_SYSTEM_PROMPT,
        input=user_content,
        text_format=OpportunitySignals,
    )

    signals = response.output_parsed

    if signals is None:
        raise RuntimeError(
            "Opportunity semantic evaluation returned no structured output."
        )

    return signals