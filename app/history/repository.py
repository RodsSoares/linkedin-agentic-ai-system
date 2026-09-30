import os
import sqlite3
from pathlib import Path
from typing import Any

from psycopg import Connection
from psycopg.rows import dict_row

from app.config.database import (
    get_database_url,
    is_postgres_enabled,
)


DEFAULT_HISTORY_DB_PATH = Path(
    os.getenv(
        "RUN_HISTORY_DB_PATH",
        "data/history/run_history.db",
    )
)


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS workflow_runs (
    run_id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    theme TEXT,
    status TEXT NOT NULL,
    opportunity_title TEXT,
    opportunity_url TEXT,
    opportunity_score REAL,
    classification TEXT,
    content_mode TEXT,
    selected_perspective_id TEXT,
    final_refinement_action TEXT,
    final_draft TEXT,
    state_json TEXT NOT NULL
)
"""

CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_workflow_runs_created_at
ON workflow_runs(created_at DESC)
"""


class SQLiteRunHistoryRepository:
    def __init__(
        self,
        database_path: str | Path = DEFAULT_HISTORY_DB_PATH,
    ) -> None:
        self.database_path = Path(database_path)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self._connect() as connection:
            connection.execute(CREATE_TABLE_SQL)
            connection.execute(CREATE_INDEX_SQL)
            connection.commit()

    def save(self, values: tuple[Any, ...]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO workflow_runs (
                    run_id, thread_id, created_at, completed_at, theme, status,
                    opportunity_title, opportunity_url, opportunity_score,
                    classification, content_mode, selected_perspective_id,
                    final_refinement_action, final_draft, state_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    completed_at=excluded.completed_at,
                    theme=excluded.theme,
                    status=excluded.status,
                    opportunity_title=excluded.opportunity_title,
                    opportunity_url=excluded.opportunity_url,
                    opportunity_score=excluded.opportunity_score,
                    classification=excluded.classification,
                    content_mode=excluded.content_mode,
                    selected_perspective_id=excluded.selected_perspective_id,
                    final_refinement_action=excluded.final_refinement_action,
                    final_draft=excluded.final_draft,
                    state_json=excluded.state_json
                """,
                values,
            )
            connection.commit()

    def load_recent(
        self,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM workflow_runs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def get(
        self,
        run_id: str,
    ) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM workflow_runs
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()

        return dict(row) if row else None

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path,
            timeout=10,
        )
        connection.row_factory = sqlite3.Row
        return connection


class PostgresRunHistoryRepository:
    def __init__(
        self,
        database_url: str | None = None,
    ) -> None:
        self.database_url = database_url or get_database_url()

        if not self.database_url:
            raise RuntimeError(
                "DATABASE_URL is required for PostgreSQL Run History"
            )

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(CREATE_TABLE_SQL)
            connection.execute(CREATE_INDEX_SQL)

    def save(self, values: tuple[Any, ...]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO workflow_runs (
                    run_id, thread_id, created_at, completed_at, theme, status,
                    opportunity_title, opportunity_url, opportunity_score,
                    classification, content_mode, selected_perspective_id,
                    final_refinement_action, final_draft, state_json
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                ON CONFLICT(run_id) DO UPDATE SET
                    completed_at=excluded.completed_at,
                    theme=excluded.theme,
                    status=excluded.status,
                    opportunity_title=excluded.opportunity_title,
                    opportunity_url=excluded.opportunity_url,
                    opportunity_score=excluded.opportunity_score,
                    classification=excluded.classification,
                    content_mode=excluded.content_mode,
                    selected_perspective_id=excluded.selected_perspective_id,
                    final_refinement_action=excluded.final_refinement_action,
                    final_draft=excluded.final_draft,
                    state_json=excluded.state_json
                """,
                values,
            )

    def load_recent(
        self,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM workflow_runs
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def get(
        self,
        run_id: str,
    ) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM workflow_runs
                WHERE run_id = %s
                """,
                (run_id,),
            ).fetchone()

        return dict(row) if row else None

    def _connect(self) -> Connection:
        return Connection.connect(
            self.database_url,
            autocommit=True,
            row_factory=dict_row,
        )


def build_run_history_repository(
    database_path: str | Path = DEFAULT_HISTORY_DB_PATH,
) -> SQLiteRunHistoryRepository | PostgresRunHistoryRepository:
    if is_postgres_enabled():
        return PostgresRunHistoryRepository()

    return SQLiteRunHistoryRepository(database_path)
