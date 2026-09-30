import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from psycopg import Connection
from psycopg.rows import dict_row

from app.config.database import get_database_url
from app.memory.models import (
    InteractionRecord,
    InteractionStatus,
)


DEFAULT_DATABASE_PATH = Path("data/memory/interaction_memory.db")


class SQLiteInteractionMemoryRepository:
    """
    SQLite persistence layer for Interaction Memory.

    This class owns persistence only.
    URL normalization and higher-level memory behavior belong to the
    service layer.
    """

    def __init__(
        self,
        database_path: str | Path = DEFAULT_DATABASE_PATH,
    ) -> None:
        self.database_path = Path(database_path)

    def initialize(self) -> None:
        """
        Create the database directory and interaction_history table
        when they do not already exist.
        """

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS interaction_history (
                    canonical_url TEXT PRIMARY KEY,
                    original_url TEXT NOT NULL,
                    visited_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    agentic_draft TEXT,
                    human_final TEXT,
                    status TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                    idx_interaction_history_visited_at
                ON interaction_history(visited_at DESC)
                """
            )

            connection.commit()

    def exists(self, canonical_url: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM interaction_history
                WHERE canonical_url = ?
                LIMIT 1
                """,
                (canonical_url,),
            ).fetchone()

        return row is not None

    def create_visit(
        self,
        canonical_url: str,
        original_url: str,
    ) -> InteractionRecord:
        """
        Persist a successfully visited URL.

        canonical_url is unique. Calling create_visit again for the same
        canonical URL does not create a duplicate record.
        """

        now = _utc_now()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO interaction_history (
                    canonical_url,
                    original_url,
                    visited_at,
                    updated_at,
                    agentic_draft,
                    human_final,
                    status
                )
                VALUES (?, ?, ?, ?, NULL, NULL, ?)
                """,
                (
                    canonical_url,
                    original_url,
                    _serialize_datetime(now),
                    _serialize_datetime(now),
                    InteractionStatus.VISITED.value,
                ),
            )

            connection.commit()

        record = self.get(canonical_url)

        if record is None:
            raise RuntimeError(
                "interaction record could not be loaded after creation"
            )

        return record

    def get(
        self,
        canonical_url: str,
    ) -> InteractionRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    canonical_url,
                    original_url,
                    visited_at,
                    updated_at,
                    agentic_draft,
                    human_final,
                    status
                FROM interaction_history
                WHERE canonical_url = ?
                """,
                (canonical_url,),
            ).fetchone()

        if row is None:
            return None

        return _row_to_record(row)

    def update_agentic_draft(
        self,
        canonical_url: str,
        draft: str,
    ) -> None:
        if not draft.strip():
            raise ValueError("draft must not be empty")

        self._update_record(
            canonical_url=canonical_url,
            assignments={
                "agentic_draft": draft,
                "status": InteractionStatus.DRAFTED.value,
            },
        )

    def update_human_final(
        self,
        canonical_url: str,
        human_final: str,
        *,
        approved: bool = False,
    ) -> None:
        if not human_final.strip():
            raise ValueError("human_final must not be empty")

        status = (
            InteractionStatus.HUMAN_APPROVED
            if approved
            else InteractionStatus.HUMAN_REVISED
        )

        self._update_record(
            canonical_url=canonical_url,
            assignments={
                "human_final": human_final,
                "status": status.value,
            },
        )

    def update_status(
        self,
        canonical_url: str,
        status: InteractionStatus,
    ) -> None:
        self._update_record(
            canonical_url=canonical_url,
            assignments={
                "status": status.value,
            },
        )

    def get_recent(
        self,
        limit: int = 20,
    ) -> list[InteractionRecord]:
        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    canonical_url,
                    original_url,
                    visited_at,
                    updated_at,
                    agentic_draft,
                    human_final,
                    status
                FROM interaction_history
                ORDER BY visited_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [_row_to_record(row) for row in rows]

    def _update_record(
        self,
        canonical_url: str,
        assignments: dict[str, str],
    ) -> None:
        allowed_columns = {
            "agentic_draft",
            "human_final",
            "status",
        }

        unsupported_columns = set(assignments) - allowed_columns

        if unsupported_columns:
            raise ValueError(
                f"unsupported update columns: "
                f"{sorted(unsupported_columns)}"
            )

        if not assignments:
            return

        assignments = {
            **assignments,
            "updated_at": _serialize_datetime(_utc_now()),
        }

        set_clause = ", ".join(
            f"{column} = ?"
            for column in assignments
        )

        values = list(assignments.values())
        values.append(canonical_url)

        with self._connect() as connection:
            cursor = connection.execute(
                f"""
                UPDATE interaction_history
                SET {set_clause}
                WHERE canonical_url = ?
                """,
                values,
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    f"interaction not found: {canonical_url}"
                )

            connection.commit()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path
        )
        connection.row_factory = sqlite3.Row
        return connection


class PostgresInteractionMemoryRepository:
    """
    PostgreSQL persistence layer for Interaction Memory.
    """

    def __init__(
        self,
        database_url: str | None = None,
    ) -> None:
        self.database_url = database_url or get_database_url()

        if not self.database_url:
            raise RuntimeError(
                "DATABASE_URL is required for PostgreSQL "
                "Interaction Memory"
            )

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS interaction_history (
                    canonical_url TEXT PRIMARY KEY,
                    original_url TEXT NOT NULL,
                    visited_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    agentic_draft TEXT,
                    human_final TEXT,
                    status TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                    idx_interaction_history_visited_at
                ON interaction_history(visited_at DESC)
                """
            )

    def exists(self, canonical_url: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM interaction_history
                WHERE canonical_url = %s
                LIMIT 1
                """,
                (canonical_url,),
            ).fetchone()

        return row is not None

    def create_visit(
        self,
        canonical_url: str,
        original_url: str,
    ) -> InteractionRecord:
        now = _utc_now()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO interaction_history (
                    canonical_url,
                    original_url,
                    visited_at,
                    updated_at,
                    agentic_draft,
                    human_final,
                    status
                )
                VALUES (%s, %s, %s, %s, NULL, NULL, %s)
                ON CONFLICT (canonical_url) DO NOTHING
                """,
                (
                    canonical_url,
                    original_url,
                    _serialize_datetime(now),
                    _serialize_datetime(now),
                    InteractionStatus.VISITED.value,
                ),
            )

        record = self.get(canonical_url)

        if record is None:
            raise RuntimeError(
                "interaction record could not be loaded after creation"
            )

        return record

    def get(
        self,
        canonical_url: str,
    ) -> InteractionRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    canonical_url,
                    original_url,
                    visited_at,
                    updated_at,
                    agentic_draft,
                    human_final,
                    status
                FROM interaction_history
                WHERE canonical_url = %s
                """,
                (canonical_url,),
            ).fetchone()

        if row is None:
            return None

        return _row_to_record(row)

    def update_agentic_draft(
        self,
        canonical_url: str,
        draft: str,
    ) -> None:
        if not draft.strip():
            raise ValueError("draft must not be empty")

        self._update_record(
            canonical_url=canonical_url,
            assignments={
                "agentic_draft": draft,
                "status": InteractionStatus.DRAFTED.value,
            },
        )

    def update_human_final(
        self,
        canonical_url: str,
        human_final: str,
        *,
        approved: bool = False,
    ) -> None:
        if not human_final.strip():
            raise ValueError("human_final must not be empty")

        status = (
            InteractionStatus.HUMAN_APPROVED
            if approved
            else InteractionStatus.HUMAN_REVISED
        )

        self._update_record(
            canonical_url=canonical_url,
            assignments={
                "human_final": human_final,
                "status": status.value,
            },
        )

    def update_status(
        self,
        canonical_url: str,
        status: InteractionStatus,
    ) -> None:
        self._update_record(
            canonical_url=canonical_url,
            assignments={
                "status": status.value,
            },
        )

    def get_recent(
        self,
        limit: int = 20,
    ) -> list[InteractionRecord]:
        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    canonical_url,
                    original_url,
                    visited_at,
                    updated_at,
                    agentic_draft,
                    human_final,
                    status
                FROM interaction_history
                ORDER BY visited_at DESC
                LIMIT %s
                """,
                (limit,),
            ).fetchall()

        return [_row_to_record(row) for row in rows]

    def _update_record(
        self,
        canonical_url: str,
        assignments: dict[str, str],
    ) -> None:
        allowed_columns = {
            "agentic_draft",
            "human_final",
            "status",
        }

        unsupported_columns = set(assignments) - allowed_columns

        if unsupported_columns:
            raise ValueError(
                f"unsupported update columns: "
                f"{sorted(unsupported_columns)}"
            )

        if not assignments:
            return

        assignments = {
            **assignments,
            "updated_at": _serialize_datetime(_utc_now()),
        }

        set_clause = ", ".join(
            f"{column} = %s"
            for column in assignments
        )

        values = list(assignments.values())
        values.append(canonical_url)

        with self._connect() as connection:
            cursor = connection.execute(
                f"""
                UPDATE interaction_history
                SET {set_clause}
                WHERE canonical_url = %s
                """,
                values,
            )

            if cursor.rowcount == 0:
                raise KeyError(
                    f"interaction not found: {canonical_url}"
                )

    def _connect(self) -> Connection:
        return Connection.connect(
            self.database_url,
            autocommit=True,
            row_factory=dict_row,
        )


def build_interaction_memory_repository(
    database_path: str | Path = DEFAULT_DATABASE_PATH,
) -> SQLiteInteractionMemoryRepository | PostgresInteractionMemoryRepository:
    """
    Build the Interaction Memory repository for the configured backend.
    """

    from app.config.database import is_postgres_enabled

    if is_postgres_enabled():
        return PostgresInteractionMemoryRepository()

    return SQLiteInteractionMemoryRepository(database_path)


# Backward-compatible public repository.
# Existing callers and tests continue to use SQLite explicitly.
InteractionMemoryRepository = SQLiteInteractionMemoryRepository


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _serialize_datetime(value: datetime) -> str:
    return value.isoformat()


def _deserialize_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value

    return datetime.fromisoformat(value)


def _row_to_record(
    row: Any,
) -> InteractionRecord:
    return InteractionRecord(
        canonical_url=row["canonical_url"],
        original_url=row["original_url"],
        visited_at=_deserialize_datetime(
            row["visited_at"]
        ),
        updated_at=_deserialize_datetime(
            row["updated_at"]
        ),
        agentic_draft=row["agentic_draft"],
        human_final=row["human_final"],
        status=InteractionStatus(
            row["status"]
        ),
    )