from pathlib import Path

import pytest

from app.memory.models import InteractionStatus
from app.memory.repository import InteractionMemoryRepository
from app.memory.service import InteractionMemoryService
from app.memory.url_normalization import canonicalize_url


def make_service(tmp_path: Path) -> InteractionMemoryService:
    database_path = tmp_path / "interaction_memory.db"

    return InteractionMemoryService(
        database_path=database_path
    )


def test_canonicalize_url_removes_tracking_parameters_and_fragment():
    url = (
        "https://Example.com/article/"
        "?utm_source=linkedin&utm_campaign=test#comments"
    )

    result = canonicalize_url(url)

    assert result == "https://example.com/article"


def test_canonicalize_url_preserves_functional_query_parameters():
    url = "https://example.com/article?id=123&utm_source=linkedin"

    result = canonicalize_url(url)

    assert result == "https://example.com/article?id=123"


def test_canonicalize_url_sorts_remaining_query_parameters():
    url = "https://example.com/article?b=2&a=1"

    result = canonicalize_url(url)

    assert result == "https://example.com/article?a=1&b=2"


def test_canonicalize_url_removes_default_https_port():
    url = "https://example.com:443/article"

    result = canonicalize_url(url)

    assert result == "https://example.com/article"


def test_canonicalize_url_preserves_non_default_port():
    url = "https://example.com:8443/article"

    result = canonicalize_url(url)

    assert result == "https://example.com:8443/article"


def test_canonicalize_url_rejects_empty_url():
    with pytest.raises(ValueError):
        canonicalize_url("")


def test_canonicalize_url_rejects_non_http_scheme():
    with pytest.raises(ValueError):
        canonicalize_url("ftp://example.com/article")


def test_canonicalize_url_rejects_credentials():
    with pytest.raises(ValueError):
        canonicalize_url(
            "https://user:password@example.com/article"
        )


def test_repository_initializes_database(tmp_path):
    database_path = tmp_path / "memory.db"

    repository = InteractionMemoryRepository(
        database_path=database_path
    )

    repository.initialize()

    assert database_path.exists()


def test_record_visit_persists_interaction(tmp_path):
    service = make_service(tmp_path)

    url = "https://example.com/article"

    record = service.record_visit(url)

    assert record.original_url == url
    assert record.canonical_url == url
    assert record.status == InteractionStatus.VISITED
    assert record.agentic_draft is None
    assert record.human_final is None


def test_has_seen_returns_false_for_unknown_url(tmp_path):
    service = make_service(tmp_path)

    assert (
        service.has_seen(
            "https://example.com/unknown"
        )
        is False
    )


def test_has_seen_returns_true_after_visit(tmp_path):
    service = make_service(tmp_path)

    url = "https://example.com/article"

    service.record_visit(url)

    assert service.has_seen(url) is True


def test_memory_persists_between_service_instances(tmp_path):
    database_path = tmp_path / "persistent_memory.db"

    first_service = InteractionMemoryService(
        database_path=database_path
    )

    url = "https://example.com/article"

    first_service.record_visit(url)

    second_service = InteractionMemoryService(
        database_path=database_path
    )

    assert second_service.has_seen(url) is True


def test_equivalent_tracking_urls_are_treated_as_same_interaction(
    tmp_path,
):
    service = make_service(tmp_path)

    first_url = (
        "https://example.com/article"
        "?utm_source=linkedin#comments"
    )

    second_url = (
        "https://example.com/article"
        "?utm_source=google"
    )

    service.record_visit(first_url)

    assert service.has_seen(second_url) is True


def test_record_visit_does_not_duplicate_same_canonical_url(
    tmp_path,
):
    service = make_service(tmp_path)

    first_url = (
        "https://example.com/article"
        "?utm_source=linkedin"
    )

    second_url = (
        "https://example.com/article"
        "?utm_source=google"
    )

    first_record = service.record_visit(first_url)
    second_record = service.record_visit(second_url)

    recent = service.get_recent(limit=20)

    assert len(recent) == 1

    assert (
        first_record.canonical_url
        == second_record.canonical_url
    )


def test_save_agentic_draft_updates_existing_record(tmp_path):
    service = make_service(tmp_path)

    url = "https://example.com/article"

    service.record_visit(url)

    service.save_agentic_draft(
        url,
        "This is the proposed comment.",
    )

    record = service.get(url)

    assert record is not None
    assert (
        record.agentic_draft
        == "This is the proposed comment."
    )
    assert record.status == InteractionStatus.DRAFTED


def test_save_human_final_updates_existing_record(tmp_path):
    service = make_service(tmp_path)

    url = "https://example.com/article"

    service.record_visit(url)

    service.save_human_final(
        url,
        "This is Rodrigo's final version.",
    )

    record = service.get(url)

    assert record is not None
    assert (
        record.human_final
        == "This is Rodrigo's final version."
    )
    assert (
        record.status
        == InteractionStatus.HUMAN_REVISED
    )


def test_save_human_final_can_mark_interaction_as_approved(
    tmp_path,
):
    service = make_service(tmp_path)

    url = "https://example.com/article"

    service.record_visit(url)

    service.save_human_final(
        url,
        "Approved version.",
        approved=True,
    )

    record = service.get(url)

    assert record is not None
    assert (
        record.status
        == InteractionStatus.HUMAN_APPROVED
    )


def test_mark_selected_updates_status(tmp_path):
    service = make_service(tmp_path)

    url = "https://example.com/article"

    service.record_visit(url)

    service.mark_selected(url)

    record = service.get(url)

    assert record is not None
    assert (
        record.status
        == InteractionStatus.SELECTED
    )


def test_get_recent_returns_requested_limit(tmp_path):
    service = make_service(tmp_path)

    service.record_visit(
        "https://example.com/article-1"
    )
    service.record_visit(
        "https://example.com/article-2"
    )
    service.record_visit(
        "https://example.com/article-3"
    )

    recent = service.get_recent(limit=2)

    assert len(recent) == 2


def test_get_recent_rejects_non_positive_limit(tmp_path):
    service = make_service(tmp_path)

    with pytest.raises(ValueError):
        service.get_recent(limit=0)


def test_filter_unseen_urls_removes_persisted_urls(tmp_path):
    service = make_service(tmp_path)

    known_url = "https://example.com/known"
    new_url = "https://example.com/new"

    service.record_visit(known_url)

    result = service.filter_unseen_urls(
        [
            known_url,
            new_url,
        ]
    )

    assert result == [new_url]


def test_filter_unseen_urls_preserves_input_order(tmp_path):
    service = make_service(tmp_path)

    urls = [
        "https://example.com/article-1",
        "https://example.com/article-2",
        "https://example.com/article-3",
    ]

    result = service.filter_unseen_urls(urls)

    assert result == urls


def test_filter_unseen_urls_removes_equivalent_duplicates(
    tmp_path,
):
    service = make_service(tmp_path)

    urls = [
        (
            "https://example.com/article"
            "?utm_source=linkedin"
        ),
        (
            "https://example.com/article"
            "?utm_source=google"
        ),
        "https://example.com/other",
    ]

    result = service.filter_unseen_urls(urls)

    assert result == [
        (
            "https://example.com/article"
            "?utm_source=linkedin"
        ),
        "https://example.com/other",
    ]


def test_filter_unseen_urls_returns_empty_list_when_all_are_known(
    tmp_path,
):
    service = make_service(tmp_path)

    first_url = "https://example.com/article-1"
    second_url = "https://example.com/article-2"

    service.record_visit(first_url)
    service.record_visit(second_url)

    result = service.filter_unseen_urls(
        [
            first_url,
            second_url,
        ]
    )

    assert result == []


def test_updating_unknown_interaction_raises_key_error(tmp_path):
    service = make_service(tmp_path)

    with pytest.raises(KeyError):
        service.save_agentic_draft(
            "https://example.com/unknown",
            "Draft",
        )


def test_empty_agentic_draft_is_rejected(tmp_path):
    service = make_service(tmp_path)

    url = "https://example.com/article"

    service.record_visit(url)

    with pytest.raises(ValueError):
        service.save_agentic_draft(
            url,
            "   ",
        )


def test_empty_human_final_is_rejected(tmp_path):
    service = make_service(tmp_path)

    url = "https://example.com/article"

    service.record_visit(url)

    with pytest.raises(ValueError):
        service.save_human_final(
            url,
            "   ",
        )
        