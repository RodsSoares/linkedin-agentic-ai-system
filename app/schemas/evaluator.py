from typing import Literal

from pydantic import BaseModel

from app.schemas.post import PostCandidate


class EvaluatorInput(BaseModel):
    post: PostCandidate
    current_draft: str
    research_result: dict | None = None


class QualityEvaluation(BaseModel):
    factual_accuracy: int
    relevance: int
    voice_match: int
    decision: Literal["PASS", "REVISE", "REJECT"]
    revision_instruction: str | None = None