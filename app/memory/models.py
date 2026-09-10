from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class InteractionStatus(StrEnum):
    VISITED = "VISITED"
    SELECTED = "SELECTED"
    DRAFTED = "DRAFTED"
    HUMAN_REVISED = "HUMAN_REVISED"
    HUMAN_APPROVED = "HUMAN_APPROVED"


class InteractionRecord(BaseModel):
    """
    Persistent representation of one discovered interaction source.

    canonical_url is the stable identity used for deduplication.
    original_url preserves the URL exactly as it was first observed.
    """

    model_config = ConfigDict(frozen=True)

    canonical_url: str
    original_url: str

    visited_at: datetime
    updated_at: datetime

    agentic_draft: str | None = None
    human_final: str | None = None

    status: InteractionStatus = InteractionStatus.VISITED