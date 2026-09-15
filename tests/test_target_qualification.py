import pytest

from app.components.target_qualification import qualify_target


@pytest.mark.parametrize(
    "url",
    [
        "https://www.linkedin.com/posts/example-ai-agents-activity-123",
        "https://linkedin.com/posts/example-ai-agents-activity-123/",
        "https://www.linkedin.com/feed/update/urn:li:activity:123",
    ],
)
def test_linkedin_post_urls_are_interaction_targets(
    url: str,
) -> None:
    result = qualify_target(url)

    assert result.target_type == "INTERACTION_TARGET"
    assert result.is_interaction_target is True


@pytest.mark.parametrize(
    ("url", "expected_type"),
    [
        (
            "https://www.linkedin.com/pulse/example-article",
            "LINKEDIN_CONTENT",
        ),
        (
            "https://www.linkedin.com/top-content/artificial-intelligence",
            "LINKEDIN_CONTENT",
        ),
        (
            "https://www.linkedin.com/company/example",
            "LINKEDIN_NON_INTERACTION",
        ),
        (
            "https://www.linkedin.com/learning/example-course",
            "LINKEDIN_NON_INTERACTION",
        ),
    ],
)
def test_known_non_interaction_linkedin_urls_are_rejected(
    url: str,
    expected_type: str,
) -> None:
    result = qualify_target(url)

    assert result.target_type == expected_type
    assert result.is_interaction_target is False


@pytest.mark.parametrize(
    "url",
    [
        "https://www.coursera.org/learn/ai",
        "https://example.com/article",
        "https://beam.ai/integrations/linkedin",
    ],
)
def test_external_urls_are_not_interaction_targets(
    url: str,
) -> None:
    result = qualify_target(url)

    assert result.target_type == "EXTERNAL_CONTENT"
    assert result.is_interaction_target is False


def test_unknown_linkedin_url_is_not_silently_accepted() -> None:
    result = qualify_target(
        "https://www.linkedin.com/in/example-person"
    )

    assert result.target_type == "UNKNOWN"
    assert result.is_interaction_target is False


def test_empty_url_is_unknown() -> None:
    result = qualify_target("")

    assert result.target_type == "UNKNOWN"
    assert result.is_interaction_target is False


def test_host_spoofing_is_not_treated_as_linkedin() -> None:
    result = qualify_target(
        "https://linkedin.com.example.org/posts/fake"
    )

    assert result.target_type == "EXTERNAL_CONTENT"
    assert result.is_interaction_target is False
    