from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.post import PostCandidate
from app.schemas.tools import SearchResult


class ScoutSelection(BaseModel):
    reason: str


class ScoutAction(BaseModel):
    action: Literal["SEARCH", "READ", "SELECT", "FINISH"]
    query: str | None = None
    url: str | None = None
    reason: str
    selection: ScoutSelection | None = None


class ScoutState(BaseModel):
    objective: str

    search_queries: list[str] = Field(default_factory=list)
    visited_urls: list[str] = Field(default_factory=list)
    candidates: list[PostCandidate] = Field(default_factory=list)

    search_results: list[SearchResult] = Field(default_factory=list)
    last_read_content: str | None = None
    last_read_url: str | None = None
    last_error: str | None = None

    last_search_outcome: Literal[
        "HAS_NOVEL_RESULTS",
        "NO_SEARCH_RESULTS",
        "NO_NOVEL_RESULTS",
    ] | None = None

    novelty_search_attempts: int = Field(default=0, ge=0)
    max_novelty_search_attempts: int = Field(default=3, ge=1)

    steps: int = Field(default=0, ge=0)
    max_steps: int = Field(default=24, ge=1)
    max_searches: int = Field(default=8, ge=1)
    max_reads: int = Field(default=8, ge=1)
    read_attempts: int = Field(default=0, ge=0)
    successful_reads: int = Field(default=0, ge=0)
    blocked_reads: int = Field(default=0, ge=0)
    sources_discovered: int = Field(default=0, ge=0)
    already_seen: int = Field(default=0, ge=0)
    diversification_count: int = Field(default=0, ge=0)
    search_strategy: str = "primary"
    blocked_urls: list[str] = Field(default_factory=list)

    status: Literal[
        "READY",
        "SEARCHING",
        "READING",
        "FINISHED",
        "FAILED",
    ] = "READY"
