from pydantic import BaseModel, Field

from app.schemas.research import EvidenceItem


class ArgumentBrief(BaseModel):
    """
    Structured intellectual synthesis produced from a ResearchBrief.

    ArgumentBrief does not define the user's final position and does not
    generate publication-ready content. It organizes the researched decision
    space so that defensible perspectives can be generated downstream.
    """

    original_thesis: str = Field(
        min_length=1,
        description=(
            "Concise statement of the central thesis or claim in the "
            "original professional discussion."
        ),
    )

    relevant_context: list[str] = Field(
        default_factory=list,
        description=(
            "Context required to understand the discussion and the "
            "intellectual decision space."
        ),
    )

    strongest_evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description=(
            "Strongest research evidence supporting relevant contribution "
            "directions."
        ),
    )

    strongest_counterevidence: list[EvidenceItem] = Field(
        default_factory=list,
        description=(
            "Strongest research evidence challenging, qualifying, or limiting "
            "relevant contribution directions."
        ),
    )

    central_tensions: list[str] = Field(
        default_factory=list,
        description=(
            "Material tensions, trade-offs, contradictions, assumptions, "
            "or competing interpretations identified in the evidence."
        ),
    )

    uncertainties: list[str] = Field(
        default_factory=list,
        description=(
            "Material uncertainties or unresolved questions that should "
            "constrain defensible arguments."
        ),
    )

    contribution_areas: list[str] = Field(
        default_factory=list,
        description=(
            "Areas where a useful, differentiated, and defensible "
            "contribution may be possible."
        ),
    )


class Perspective(BaseModel):
    """
    One defensible intellectual direction derived from an ArgumentBrief.

    A Perspective represents what could be worth saying, not how it should
    be stylistically expressed.
    """

    perspective_id: str = Field(
        min_length=1,
        description=(
            "Stable identifier for this perspective within the generated set."
        ),
    )

    label: str = Field(
        min_length=1,
        description=(
            "Short semantic label describing the intellectual direction."
        ),
    )

    core_argument: str = Field(
        min_length=1,
        description=(
            "Central argument represented by this perspective."
        ),
    )

    why_it_matters: str = Field(
        min_length=1,
        description=(
            "Why this perspective could add meaningful value to the discussion."
        ),
    )

    supporting_evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description=(
            "Research evidence supporting this perspective."
        ),
    )

    counterargument: str | None = Field(
        default=None,
        description=(
            "Strongest material counterargument, limitation, or challenge "
            "to this perspective."
        ),
    )

    uncertainty: str | None = Field(
        default=None,
        description=(
            "Relevant uncertainty that should qualify this perspective."
        ),
    )

    contribution: str = Field(
        min_length=1,
        description=(
            "Specific contribution this perspective could make to the "
            "professional conversation."
        ),
    )


class PerspectiveSet(BaseModel):
    """
    Bounded set of materially distinct and defensible perspectives.

    Differences between perspectives must be intellectual rather than merely
    stylistic.
    """

    perspectives: list[Perspective] = Field(
        min_length=2,
        max_length=4,
        description=(
            "Two to four materially distinct and defensible intellectual "
            "perspectives derived from the same ArgumentBrief."
        ),
    )


class SelectedPerspective(BaseModel):
    """
    Human-selected intellectual direction supplied to downstream generation.

    Human guidance may refine the selected direction without transferring
    final intellectual authority back to the model.
    """

    perspective: Perspective

    human_guidance: str | None = Field(
        default=None,
        description=(
            "Optional human guidance refining how the selected intellectual "
            "direction should be developed."
        ),
    )