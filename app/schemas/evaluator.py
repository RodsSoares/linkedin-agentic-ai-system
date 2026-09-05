from pydantic import BaseModel, Field

from app.schemas.post import PostCandidate


class EvaluatorInput(BaseModel):
    post: PostCandidate
    current_draft: str
    research_result: dict | None = None


class VoiceEvaluation(BaseModel):
    naturalness: int = Field(ge=0, le=100)
    directness: int = Field(ge=0, le=100)
    practical_insight: int = Field(ge=0, le=100)
    professional_maturity: int = Field(ge=0, le=100)
    business_technology_fit: int = Field(ge=0, le=100)
    anti_cliche: int = Field(ge=0, le=100)
    non_promotional: int = Field(ge=0, le=100)


class EvaluationSignals(BaseModel):
    factual_accuracy: int = Field(ge=0, le=100)
    relevance: int = Field(ge=0, le=100)
    voice: VoiceEvaluation
    revision_instruction: str | None = None


class QualityEvaluation(BaseModel):
    factual_accuracy: int = Field(ge=0, le=100)
    relevance: int = Field(ge=0, le=100)
    voice_match: int = Field(ge=0, le=100)
    decision: str
    revision_instruction: str | None = None