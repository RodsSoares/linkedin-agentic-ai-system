from typing import TypedDict

from app.schemas.evaluator import QualityEvaluation
from app.schemas.opportunity import OpportunityEvaluation
from app.schemas.post import PostCandidate
from app.schemas.research import ResearchBrief
from app.schemas.argument import ArgumentBrief, PerspectiveSet, SelectedPerspective


class LinkedInAgentState(TypedDict):
    scout_objective: str | None
    post: PostCandidate | None
    opportunity_evaluation: OpportunityEvaluation | None
    research_result: ResearchBrief | None
    argument_brief: ArgumentBrief | None
    perspective_set: PerspectiveSet | None
    selected_perspective: SelectedPerspective | None
    current_draft: str | None
    quality_evaluation: QualityEvaluation | None
    iteration: int
    next_step: str | None
    human_feedback: str | None
    status: str