from pydantic import BaseModel

from app.schemas.post import PostCandidate
from app.schemas.research import ResearchBrief


class WriterInput(BaseModel):
    post: PostCandidate
    research_result: ResearchBrief | None = None
    previous_draft: str | None = None
    revision_instruction: str | None = None
