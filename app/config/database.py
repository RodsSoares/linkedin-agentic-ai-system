import os


def get_database_url() -> str | None:
    """
    Return the configured PostgreSQL database URL.
    """
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        return None

    return database_url.strip() or None


def get_persistence_backend() -> str:
    """
    Return the configured persistence backend.

    Defaults to local so development and tests remain isolated
    even when DATABASE_URL exists in the environment.
    """
    return os.getenv("PERSISTENCE_BACKEND", "local").strip().lower()


def is_postgres_enabled() -> bool:
    """
    Return whether PostgreSQL persistence is explicitly enabled.
    """
    return (
        get_persistence_backend() == "postgres"
        and get_database_url() is not None
    )