from pathlib import Path

from app.memory.models import (
    InteractionRecord,
    InteractionStatus,
)
from app.memory.repository import (
    DEFAULT_DATABASE_PATH,
    InteractionMemoryRepository,
)
from app.memory.url_normalization import (
    canonicalize_url,
)


class InteractionMemoryService:
    """
    Application-facing interface for persistent interaction memory.

    Consumers such as Scout should use this service instead of accessing
    SQLite or URL-normalization behavior directly.
    """

    def __init__(
        self,
        repository: InteractionMemoryRepository | None = None,
        *,
        database_path: str | Path = DEFAULT_DATABASE_PATH,
    ) -> None:
        self.repository = (
            repository
            if repository is not None
            else InteractionMemoryRepository(database_path)
        )

        self.repository.initialize()

    def has_seen(self, url: str) -> bool:
        canonical_url = canonicalize_url(url)

        return self.repository.exists(
            canonical_url
        )

    def record_visit(
        self,
        url: str,
    ) -> InteractionRecord:
        """
        Record a successfully read URL.

        This method should only be called after READ completes
        successfully.
        """

        canonical_url = canonicalize_url(url)

        return self.repository.create_visit(
            canonical_url=canonical_url,
            original_url=url,
        )

    def mark_selected(
        self,
        url: str,
    ) -> None:
        canonical_url = canonicalize_url(url)

        self.repository.update_status(
            canonical_url,
            InteractionStatus.SELECTED,
        )

    def save_agentic_draft(
        self,
        url: str,
        draft: str,
    ) -> None:
        canonical_url = canonicalize_url(url)

        self.repository.update_agentic_draft(
            canonical_url,
            draft,
        )

    def save_human_final(
        self,
        url: str,
        text: str,
        *,
        approved: bool = False,
    ) -> None:
        canonical_url = canonicalize_url(url)

        self.repository.update_human_final(
            canonical_url,
            text,
            approved=approved,
        )

    def get(
        self,
        url: str,
    ) -> InteractionRecord | None:
        canonical_url = canonicalize_url(url)

        return self.repository.get(
            canonical_url
        )

    def get_recent(
        self,
        limit: int = 20,
    ) -> list[InteractionRecord]:
        """
        Return the most recently visited interactions.

        This interface can later feed the frontend's recent-history view.
        """

        return self.repository.get_recent(
            limit=limit
        )

    def filter_unseen_urls(
        self,
        urls: list[str],
    ) -> list[str]:
        """
        Return only URLs that are not already present in persistent
        interaction memory.

        Ordering from the original input is preserved.
        """

        unseen_urls: list[str] = []
        seen_in_batch: set[str] = set()

        for url in urls:
            canonical_url = canonicalize_url(url)

            if canonical_url in seen_in_batch:
                continue

            seen_in_batch.add(canonical_url)

            if self.repository.exists(
                canonical_url
            ):
                continue

            unseen_urls.append(url)

        return unseen_urls
    