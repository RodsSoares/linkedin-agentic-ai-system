import pytest

from app.inputs.target_content import load_target_content


def test_load_target_content_builds_post_candidate_from_read_content():
    captured_urls: list[str] = []

    def fake_reader(url: str) -> str:
        captured_urls.append(url)
        return (
            "Before automating a process, understand why it exists, "
            "where the bottlenecks are, and what outcome should improve."
        )

    candidate = load_target_content(
        "https://www.linkedin.com/feed/update/urn:li:activity:123/",
        read_tool=fake_reader,
    )

    assert captured_urls == [
        "https://www.linkedin.com/feed/update/urn:li:activity:123/"
    ]
    assert candidate.post_id == (
        "https://www.linkedin.com/feed/update/urn:li:activity:123/"
    )
    assert candidate.post_url == (
        "https://www.linkedin.com/feed/update/urn:li:activity:123/"
    )
    assert candidate.author_name == "Unknown"
    assert candidate.source == "target_url"
    assert "Before automating a process" in candidate.post_text


def test_load_target_content_strips_surrounding_url_whitespace():
    captured_urls: list[str] = []

    def fake_reader(url: str) -> str:
        captured_urls.append(url)
        return "Useful professional content."

    candidate = load_target_content(
        "  https://example.com/post/1  ",
        read_tool=fake_reader,
    )

    assert captured_urls == ["https://example.com/post/1"]
    assert candidate.post_url == "https://example.com/post/1"


def test_load_target_content_rejects_empty_url_before_reading():
    reader_called = False

    def fake_reader(url: str) -> str:
        nonlocal reader_called
        reader_called = True
        return "Should not be read."

    with pytest.raises(ValueError, match="cannot be empty"):
        load_target_content("   ", read_tool=fake_reader)

    assert reader_called is False


def test_load_target_content_rejects_empty_prepared_content():
    def fake_reader(url: str) -> str:
        return "   \n\t   "

    with pytest.raises(ValueError, match="returned empty content"):
        load_target_content(
            "https://example.com/post/empty",
            read_tool=fake_reader,
        )
        