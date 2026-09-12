from pydantic import BaseModel, Field, field_validator

from app.schemas.editorial_preference import EditorialPreferenceEvaluation
from app.schemas.research import ResearchBrief
from app.schemas.scout import PostCandidate


class EditorialRewriteInput(BaseModel):
    source_post: PostCandidate
    research_result: ResearchBrief | None = None
    original_draft: str
    editorial_evaluation: EditorialPreferenceEvaluation
    calibration_context: str | None = None

    @field_validator("original_draft")
    @classmethod
    def validate_original_draft(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("original_draft must not be empty")
        return normalized

    @field_validator("calibration_context")
    @classmethod
    def normalize_calibration_context(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class EditorialRewriteResult(BaseModel):
    revised_draft: str = Field(min_length=1)
    preserved_elements: list[str] = Field(default_factory=list, max_length=8)
    removed_or_compressed_elements: list[str] = Field(
        default_factory=list,
        max_length=8,
    )
    rewrite_reason: str = Field(min_length=1)

    @field_validator("revised_draft")
    @classmethod
    def normalize_revised_draft(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("revised_draft must not be empty")
        return normalized
    