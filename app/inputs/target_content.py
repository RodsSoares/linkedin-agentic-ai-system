from app.config.settings import SCOUT_READ_CONTEXT_MAX_TOKENS
from app.context_preparation import prepare_context
from app.schemas.post import PostCandidate
from app.schemas.tools import ReadTool


def load_target_content(
    url: str,
    read_tool: ReadTool,
) -> PostCandidate:
    normalized_url = url.strip()

    if not normalized_url:
        raise ValueError("Target content URL cannot be empty.")

    raw_content = read_tool(normalized_url)

    prepared = prepare_context(
        raw_content,
        max_tokens=SCOUT_READ_CONTEXT_MAX_TOKENS,
    )

    if not prepared.content:
        raise ValueError("Target content reader returned empty content.")

    return PostCandidate(
        post_id=normalized_url,
        author_name="Unknown",
        post_text=prepared.content,
        post_url=normalized_url,
        source="target_url",
    )
