import pytest
from pydantic import ValidationError

from app.schemas.argument import (
    ArgumentBrief,
    ArgumentSynthesis,
    Perspective,
    PerspectiveSet,
    SelectedPerspective,
    PerspectiveSynthesis,
    PerspectiveSetSynthesis,
)
from app.schemas.research import EvidenceItem


def make_evidence(
    claim: str = "AI can reduce manual analytical work.",
) -> EvidenceItem:
    return EvidenceItem(
        claim=claim,
        support="The source provides evidence supporting the claim.",
        source_url="https://example.com/source",
        source_title="Example Source",
        relevance=90,
        confidence=85,
    )


def make_perspective(
    perspective_id: str = "operational",
    label: str = "Operational",
) -> Perspective:
    return Perspective(
        perspective_id=perspective_id,
        label=label,
        core_argument="The operational impact is more important than simple task automation.",
        why_it_matters="It reframes the discussion around how work is redesigned.",
        supporting_evidence=[make_evidence()],
        counterargument="Automation gains may remain limited in poorly designed processes.",
        uncertainty="The magnitude of the effect depends on implementation quality.",
        contribution="Connect AI adoption with process redesign and operational outcomes.",
    )


def test_argument_synthesis_accepts_valid_data():
    synthesis = ArgumentSynthesis(
        original_thesis="AI will substantially change professional work.",
        relevant_context=[
            "Adoption is occurring across multiple business functions.",
        ],
        strongest_evidence_indices=[0, 2],
        strongest_counterevidence_indices=[1],
        central_tensions=[
            "Automation efficiency versus organizational redesign.",
        ],
        uncertainties=[
            "Long-term organizational effects remain uncertain.",
        ],
        contribution_areas=[
            "Connect technological capability with operating-model change.",
        ],
    )

    assert synthesis.original_thesis == (
        "AI will substantially change professional work."
    )
    assert synthesis.strongest_evidence_indices == [0, 2]
    assert synthesis.strongest_counterevidence_indices == [1]


def test_argument_synthesis_rejects_empty_original_thesis():
    with pytest.raises(ValidationError):
        ArgumentSynthesis(
            original_thesis="",
        )


def test_argument_synthesis_optional_collections_default_to_empty():
    synthesis = ArgumentSynthesis(
        original_thesis="A valid thesis.",
    )

    assert synthesis.relevant_context == []
    assert synthesis.strongest_evidence_indices == []
    assert synthesis.strongest_counterevidence_indices == []
    assert synthesis.central_tensions == []
    assert synthesis.uncertainties == []
    assert synthesis.contribution_areas == []

def test_argument_brief_accepts_valid_data():
    evidence = make_evidence()

    brief = ArgumentBrief(
        original_thesis="AI will substantially change professional work.",
        relevant_context=[
            "Adoption is occurring across multiple business functions.",
        ],
        strongest_evidence=[evidence],
        strongest_counterevidence=[],
        central_tensions=[
            "Automation efficiency versus organizational redesign.",
        ],
        uncertainties=[
            "Long-term organizational effects remain uncertain.",
        ],
        contribution_areas=[
            "Connect technological capability with operating-model change.",
        ],
    )

    assert brief.original_thesis == (
        "AI will substantially change professional work."
    )
    assert brief.strongest_evidence == [evidence]
    assert len(brief.central_tensions) == 1


def test_argument_brief_rejects_empty_original_thesis():
    with pytest.raises(ValidationError):
        ArgumentBrief(
            original_thesis="",
        )


def test_argument_brief_optional_collections_default_to_empty():
    brief = ArgumentBrief(
        original_thesis="A valid thesis.",
    )

    assert brief.relevant_context == []
    assert brief.strongest_evidence == []
    assert brief.strongest_counterevidence == []
    assert brief.central_tensions == []
    assert brief.uncertainties == []
    assert brief.contribution_areas == []


def test_perspective_accepts_valid_data():
    perspective = make_perspective()

    assert perspective.perspective_id == "operational"
    assert perspective.label == "Operational"
    assert len(perspective.supporting_evidence) == 1


def test_perspective_rejects_empty_core_argument():
    with pytest.raises(ValidationError):
        Perspective(
            perspective_id="operational",
            label="Operational",
            core_argument="",
            why_it_matters="This matters.",
            contribution="A useful contribution.",
        )


def test_perspective_allows_optional_counterargument_and_uncertainty():
    perspective = Perspective(
        perspective_id="economic",
        label="Economic",
        core_argument="AI changes the economics of knowledge work.",
        why_it_matters="It affects how organizations allocate resources.",
        contribution="Introduce an economic perspective into the discussion.",
    )

    assert perspective.counterargument is None
    assert perspective.uncertainty is None
    assert perspective.supporting_evidence == []


def test_perspective_set_accepts_two_perspectives():
    perspective_set = PerspectiveSet(
        perspectives=[
            make_perspective("operational", "Operational"),
            make_perspective("economic", "Economic"),
        ],
    )

    assert len(perspective_set.perspectives) == 2


def test_perspective_set_accepts_four_perspectives():
    perspective_set = PerspectiveSet(
        perspectives=[
            make_perspective("operational", "Operational"),
            make_perspective("economic", "Economic"),
            make_perspective("organizational", "Organizational"),
            make_perspective("human", "Human"),
        ],
    )

    assert len(perspective_set.perspectives) == 4


def test_perspective_set_rejects_single_perspective():
    with pytest.raises(ValidationError):
        PerspectiveSet(
            perspectives=[
                make_perspective(),
            ],
        )


def test_perspective_set_rejects_more_than_four_perspectives():
    with pytest.raises(ValidationError):
        PerspectiveSet(
            perspectives=[
                make_perspective("p1", "P1"),
                make_perspective("p2", "P2"),
                make_perspective("p3", "P3"),
                make_perspective("p4", "P4"),
                make_perspective("p5", "P5"),
            ],
        )


def test_selected_perspective_preserves_human_selection():
    perspective = make_perspective()

    selected = SelectedPerspective(
        perspective=perspective,
        human_guidance=(
            "Emphasize the operational implications and avoid overstating "
            "the evidence."
        ),
    )

    assert selected.perspective == perspective
    assert selected.human_guidance is not None


def test_selected_perspective_allows_no_human_guidance():
    perspective = make_perspective()

    selected = SelectedPerspective(
        perspective=perspective,
    )

    assert selected.perspective == perspective
    assert selected.human_guidance is None


def test_perspective_set_accepts_two_distinct_perspectives():
    perspective_a = Perspective(
        perspective_id="perspective-a",
        label="Operating model",
        core_argument=(
            "AI-agent value depends on operating-model design, "
            "not technical capability alone."
        ),
        why_it_matters=(
            "Organizations may overestimate technology while "
            "underestimating workflow redesign."
        ),
        supporting_evidence=[],
        counterargument=None,
        uncertainty=None,
        contribution=(
            "Shift the discussion from agent capability to "
            "operational integration."
        ),
    )

    perspective_b = Perspective(
        perspective_id="perspective-b",
        label="Bounded autonomy",
        core_argument=(
            "Agent autonomy should be calibrated according to "
            "decision risk and reversibility."
        ),
        why_it_matters=(
            "Uniform human approval policies can create either "
            "excessive risk or unnecessary friction."
        ),
        supporting_evidence=[],
        counterargument=None,
        uncertainty=None,
        contribution=(
            "Introduce risk and reversibility as practical "
            "criteria for autonomy."
        ),
    )

    perspective_set = PerspectiveSet(
        perspectives=[
            perspective_a,
            perspective_b,
        ]
    )

    assert len(perspective_set.perspectives) == 2
    assert perspective_set.perspectives[0].perspective_id == "perspective-a"
    assert perspective_set.perspectives[1].perspective_id == "perspective-b"


def test_perspective_set_rejects_single_perspective():
    perspective = Perspective(
        perspective_id="perspective-a",
        label="Operating model",
        core_argument="AI-agent value depends on operating-model design.",
        why_it_matters="Technical capability alone is insufficient.",
        supporting_evidence=[],
        contribution="Focus discussion on operational integration.",
    )

    with pytest.raises(ValidationError):
        PerspectiveSet(
            perspectives=[perspective]
        )


def test_perspective_set_rejects_more_than_four_perspectives():
    perspectives = [
        Perspective(
            perspective_id=f"perspective-{index}",
            label=f"Perspective {index}",
            core_argument=f"Core argument {index}",
            why_it_matters=f"Why it matters {index}",
            supporting_evidence=[],
            contribution=f"Contribution {index}",
        )
        for index in range(5)
    ]

    with pytest.raises(ValidationError):
        PerspectiveSet(
            perspectives=perspectives
        )


def test_selected_perspective_preserves_human_guidance():
    perspective = Perspective(
        perspective_id="perspective-a",
        label="Bounded autonomy",
        core_argument=(
            "Autonomy should depend on decision risk and reversibility."
        ),
        why_it_matters=(
            "Different decisions justify different levels of human control."
        ),
        supporting_evidence=[],
        contribution=(
            "Use risk and reversibility to discuss autonomy boundaries."
        ),
    )

    selected = SelectedPerspective(
        perspective=perspective,
        human_guidance=(
            "Connect this with practical supply-chain decision making."
        ),
    )

    assert selected.perspective == perspective
    assert selected.human_guidance == (
        "Connect this with practical supply-chain decision making."
    )


def test_perspective_synthesis_accepts_evidence_indices():
    synthesis = PerspectiveSynthesis(
        perspective_id="bounded-autonomy",
        label="Bounded autonomy",
        core_argument=(
            "Agent autonomy should depend on decision risk "
            "and reversibility."
        ),
        why_it_matters=(
            "Different decisions justify different levels "
            "of human control."
        ),
        supporting_evidence_indices=[0, 2],
        counterargument=(
            "Additional human control can reduce automation speed."
        ),
        uncertainty=(
            "The appropriate thresholds are not yet established."
        ),
        contribution=(
            "Use risk and reversibility as criteria for autonomy."
        ),
    )

    assert synthesis.supporting_evidence_indices == [0, 2]


def test_perspective_synthesis_defaults_evidence_indices_to_empty():
    synthesis = PerspectiveSynthesis(
        perspective_id="operating-model",
        label="Operating model",
        core_argument=(
            "AI-agent value depends on operating-model design."
        ),
        why_it_matters=(
            "Technical capability alone does not guarantee value."
        ),
        contribution=(
            "Shift attention from capability to operational integration."
        ),
    )

    assert synthesis.supporting_evidence_indices == []


def test_perspective_set_synthesis_requires_two_to_four_perspectives():
    perspective = PerspectiveSynthesis(
        perspective_id="single",
        label="Single perspective",
        core_argument="A valid argument.",
        why_it_matters="It matters.",
        contribution="It contributes.",
    )

    with pytest.raises(ValidationError):
        PerspectiveSetSynthesis(
            perspectives=[perspective]
        )