from openai import OpenAI

from app.config.settings import (
    MAX_OUTPUT_TOKENS,
    MODEL_NAME,
    OPENAI_API_KEY,
)
from app.prompts.writer import WRITER_SYSTEM_PROMPT
from app.schemas.writer import WriterInput


client = OpenAI(api_key=OPENAI_API_KEY)


def writer(input_data: WriterInput) -> str:
    user_content = f"""
POST AUTHOR:
{input_data.post.author_name}

POST:
{input_data.post.post_text}

RESEARCH:
{input_data.research_result}

PREVIOUS DRAFT:
{input_data.previous_draft}

REVISION INSTRUCTION:
{input_data.revision_instruction}
""".strip()

    response = client.responses.create(
        model=MODEL_NAME,
        instructions=WRITER_SYSTEM_PROMPT,
        input=user_content,
        max_output_tokens=MAX_OUTPUT_TOKENS,
    )

    return response.output_text.strip()