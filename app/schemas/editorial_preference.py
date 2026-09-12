from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.research import ResearchBrief
from app.schemas.scout import PostCandidate


ContentIntent = Literal["COMMENT"]
EditorialDecision = Literal["PASS", "ADJUST"]


class EditorialPreferenceInput(BaseModel):
    source_post: PostCandidate
    research_result: ResearchBrief | None = None
    draft: str
    content_intent: ContentIntent = "COMMENT"
    calibration_context: str | None = None

    @field_validator("draft")
    @classmethod
    def validate_draft(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("draft must not be empty")
        return normalized

    @field_validator("calibration_context")
    @classmethod
    def normalize_calibration_context(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class EditorialPreferenceEvaluation(BaseModel):
    central_thesis_focus: int = Field(ge=0, le=100)
    contribution_density: int = Field(ge=0, le=100)
    conversational_naturalness: int = Field(ge=0, le=100)
    selective_evidence_use: int = Field(ge=0, le=100)
    stopping_discipline: int = Field(ge=0, le=100)
    front_loaded_value: int = Field(ge=0, le=100)
    synthetic_completeness_risk: int = Field(ge=0, le=100)
    publication_likelihood: int = Field(ge=0, le=100)

    core_thesis: str = Field(min_length=1)

    must_preserve_elements: list[str] = Field(default_factory=list, max_length=5)
    optional_support_elements: list[str] = Field(default_factory=list, max_length=8)
    remove_or_compress_elements: list[str] = Field(default_factory=list, max_length=8)

    editorial_reason: str = Field(min_length=1)
    decision: EditorialDecision
    