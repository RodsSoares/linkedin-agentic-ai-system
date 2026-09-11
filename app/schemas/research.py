from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.opportunity import OpportunityEvaluation
from app.schemas.post import PostCandidate
from app.schemas.tools import SearchResult


class ResearchActionType(str, Enum):
    SEARCH = "SEARCH"
    READ = "READ"
    EXTRACT = "EXTRACT"
    FINISH = "FINISH"


class ResearchStatus(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"
    LIMIT_REACHED = "LIMIT_REACHED"


class ResearchObjective(BaseModel):
    question: str = Field(
        min_length=1,
        description="Primary question that the Research capability must investigate.",
    )

    focus_areas: list[str] = Field(
        default_factory=list,
        description="Specific areas that should be covered while answering the research question.",
    )


class EvidenceItem(BaseModel):
    claim: str = Field(
        min_length=1,
        description="Factual conclusion supported by the observed source.",
    )

    support: str = Field(
        min_length=1,
        description="Concise explanation of what in the source supports the claim.",
    )

    source_url: str = Field(
        min_length=1,
        description="URL of the source from which the evidence was extracted.",
    )

    source_title: str = Field(
        min_length=1,
        description="Title of the source from which the evidence was extracted.",
    )

    relevance: int = Field(
        ge=0,
        le=100,
        description="Integer from 0 to 100 indicating relevance to the specific ResearchObjective.",
    )

    confidence: int = Field(
        ge=0,
        le=100,
        description="Integer from 0 to 100 indicating how strongly the observed source supports the recorded claim.",
    )


class ResearchAction(BaseModel):
    action: ResearchActionType

    search_query: str | None = Field(
        default=None,
        description="Search query requested when action is SEARCH.",
    )

    url: str | None = Field(
        default=None,
        description="Previously discovered URL requested when action is READ.",
    )

    evidence: EvidenceItem | None = Field(
        default=None,
        description="Evidence proposed for extraction when action is EXTRACT.",
    )

    finish_status: ResearchStatus | None = Field(
        default=None,
        description=(
            "Semantic sufficiency judgment requested when action is FINISH. "
            "Only SUFFICIENT or INSUFFICIENT may be accepted by the runtime; "
            "LIMIT_REACHED remains runtime-owned."
        ),
    )

    material_gaps: list[str] = Field(
        default_factory=list,
        description=(
            "Material evidence gaps that still prevent a defensible contribution. "
            "This is a semantic assessment, not a deterministic evidence-count rule."
        ),
    )

    next_research_goal: str | None = Field(
        default=None,
        description=(
            "Specific evidence gap the next SEARCH or READ is intended to resolve. "
            "Leave null when no further research is semantically justified."
        ),
    )

    sufficiency_reason: str | None = Field(
        default=None,
        description=(
            "Semantic explanation of why current evidence is sufficient, insufficient, "
            "or why further research is still required."
        ),
    )

    reason: str = Field(
        min_length=1,
        description="Semantic reason for requesting this action.",
    )


class ReadSource(BaseModel):
    url: str = Field(
        min_length=1,
        description="URL of a source that was actually read by the Research capability.",
    )

    title: str = Field(
        min_length=1,
        description="Title of the source that was actually read.",
    )

    content: str = Field(
        min_length=1,
        description="Observed content returned by the web reader.",
    )


class ResearchState(BaseModel):
    post: PostCandidate
    opportunity_evaluation: OpportunityEvaluation
    research_objective: ResearchObjective | None = None
    search_queries: list[str] = Field(default_factory=list)
    search_results: list[SearchResult] = Field(default_factory=list)
    visited_urls: list[str] = Field(default_factory=list)
    read_sources: list[ReadSource] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    material_gaps: list[str] = Field(default_factory=list)
    next_research_goal: str | None = None
    sufficiency_reason: str | None = None
    steps: int = Field(default=0, ge=0)
    decision_attempts: int = Field(default=0, ge=0)
    search_count: int = Field(default=0, ge=0)
    read_count: int = Field(default=0, ge=0)
    last_error: str | None = None
    status: ResearchStatus | None = None


class ResearchBriefSynthesis(BaseModel):
    """LLM-owned semantic synthesis of a completed ResearchState."""

    summary: str = Field(
        min_length=1,
        description="Concise synthesis of the research findings for the Writer.",
    )
    key_findings: list[str] = Field(default_factory=list)
    counterpoints: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)


class ResearchBrief(BaseModel):
    research_objective: ResearchObjective

    summary: str = Field(
        min_length=1,
        description="Concise synthesis of the research findings for the Writer.",
    )

    key_findings: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    counterpoints: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    sources: list[SearchResult] = Field(default_factory=list)
    status: ResearchStatus