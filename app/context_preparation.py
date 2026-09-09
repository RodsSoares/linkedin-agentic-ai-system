from dataclasses import dataclass
import re

import tiktoken

from app.config.settings import CONTEXT_TOKEN_ENCODING


@dataclass(frozen=True)
class PreparedContext:
    content: str
    original_tokens: int
    prepared_tokens: int
    truncated: bool


def _get_encoding(encoding_name: str):
    try:
        return tiktoken.get_encoding(encoding_name)
    except ValueError:
        return tiktoken.get_encoding("cl100k_base")


def count_tokens(
    text: str,
    *,
    encoding_name: str = CONTEXT_TOKEN_ENCODING,
) -> int:
    if not text:
        return 0

    encoding = _get_encoding(encoding_name)
    return len(encoding.encode(text))


def normalize_external_text(text: str) -> str:
    if not text:
        return ""

    normalized_lines: list[str] = []
    seen_lines: set[str] = set()

    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()

        if not line:
            continue

        if line in seen_lines:
            continue

        seen_lines.add(line)
        normalized_lines.append(line)

    return "\n".join(normalized_lines)


def prepare_context(
    text: str,
    *,
    max_tokens: int,
    encoding_name: str = CONTEXT_TOKEN_ENCODING,
) -> PreparedContext:
    if max_tokens <= 0:
        raise ValueError("max_tokens must be greater than zero.")

    normalized = normalize_external_text(text)
    encoding = _get_encoding(encoding_name)

    original_tokens = len(encoding.encode(normalized))

    if original_tokens <= max_tokens:
        return PreparedContext(
            content=normalized,
            original_tokens=original_tokens,
            prepared_tokens=original_tokens,
            truncated=False,
        )

    encoded = encoding.encode(normalized)
    bounded = encoded[:max_tokens]
    content = encoding.decode(bounded).strip()

    prepared_tokens = len(encoding.encode(content))

    return PreparedContext(
        content=content,
        original_tokens=original_tokens,
        prepared_tokens=prepared_tokens,
        truncated=True,
    )
