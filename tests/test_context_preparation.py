import pytest

from app.context_preparation import (
    count_tokens,
    normalize_external_text,
    prepare_context,
)


def test_normalize_external_text_removes_duplicate_lines():
    text = """
    Menu
    Article title
    Useful paragraph here.
    Menu
    Useful paragraph here.
    Footer
    """

    normalized = normalize_external_text(text)

    assert normalized.splitlines() == [
        "Menu",
        "Article title",
        "Useful paragraph here.",
        "Footer",
    ]


def test_prepare_context_enforces_hard_token_budget():
    text = "agentic supply chain " * 200

    prepared = prepare_context(
        text,
        max_tokens=40,
    )

    assert prepared.truncated is True
    assert prepared.original_tokens > 40
    assert prepared.prepared_tokens <= 40
    assert count_tokens(prepared.content) <= 40


def test_prepare_context_preserves_short_content():
    text = "Short useful source content."

    prepared = prepare_context(
        text,
        max_tokens=100,
    )

    assert prepared.content == text
    assert prepared.truncated is False
    assert prepared.prepared_tokens == prepared.original_tokens


def test_prepare_context_rejects_non_positive_budget():
    with pytest.raises(
        ValueError,
        match="max_tokens must be greater than zero",
    ):
        prepare_context(
            "content",
            max_tokens=0,
        )
