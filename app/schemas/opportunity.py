from typing import Literal

from pydantic import BaseModel, Field


class OpportunitySignals(BaseModel):
    topic_relevance: int = Field(ge=0, le=100)
    positioning_fit: int = Field(ge=0, le=100)
    contribution_potential: int = Field(ge=0, le=100)
    research_cost: int = Field(ge=0, le=100)


class OpportunityEvaluation(BaseModel):
    topic_relevance: int = Field(ge=0, le=100)
    positioning_fit: int = Field(ge=0, le=100)
    contribution_potential: int = Field(ge=0, le=100)
    engagement_potential: int = Field(ge=0, le=100)
    research_cost: int = Field(ge=0, le=100)
    research_efficiency: int = Field(ge=0, le=100)
    opportunity_score: float = Field(ge=0, le=100)
    classification: Literal["HIGH", "MEDIUM", "LOW"]