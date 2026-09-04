from pydantic import BaseModel

from app.schemas.post import PostCandidate


class WriterInput(BaseModel):
    post: PostCandidate
    research_result: dict | None = None
    previous_draft: str | None = None
    revision_instruction: str | None = None