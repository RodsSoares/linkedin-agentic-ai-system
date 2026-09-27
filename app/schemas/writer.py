from typing import Literal

from pydantic import BaseModel

from app.schemas.argument import SelectedPerspective
from app.schemas.post import PostCandidate
from app.schemas.research import ResearchBrief


ContentMode = Literal[
    "linkedin_post",
    "linkedin_reply",
    "article",
]


class WriterInput(BaseModel):
    post: PostCandidate
    research_result: ResearchBrief | None = None
    selected_perspective: SelectedPerspective | None = None
    content_mode: ContentMode = "linkedin_reply"
    previous_draft: str | None = None
    revision_instruction: str | None = None
    