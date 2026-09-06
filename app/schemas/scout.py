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

    steps: int = Field(default=0, ge=0)
    max_steps: int = Field(default=5, ge=1)

    status: Literal[
        "READY",
        "SEARCHING",
        "READING",
        "FINISHED",
        "FAILED",
    ] = "READY"