from typing import TypedDict

from app.schemas.post import PostCandidate

from app.schemas.evaluator import QualityEvaluation


class LinkedInAgentState(TypedDict):
    post: PostCandidate | None
    opportunity_score: int | None
    research_result: dict | None
    current_draft: str | None
    quality_evaluation: QualityEvaluation | None
    iteration: int
    next_step: str | None
    human_feedback: str | None
    status: str