from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import Command

from app.graph.nodes.human_perspective_selection_node import (
    human_perspective_selection_node,
)
from app.graph.state import LinkedInAgentState
from app.schemas.argument import Perspective, PerspectiveSet


def _make_perspective_set() -> PerspectiveSet:
    return PerspectiveSet(
        perspectives=[
            Perspective(
                perspective_id="operating-model",
                label="Operating model",
                core_argument=(
                    "AI-agent value depends on operating-model design."
                ),
                why_it_matters=(
                    "Technical capability alone does not guarantee "
                    "operational value."
                ),
                supporting_evidence=[],
                counterargument=None,
                uncertainty=None,
                contribution=(
                    "Shift attention from capability to operational integration."
                ),
            ),
            Perspective(
                perspective_id="risk-calibrated-autonomy",
                label="Risk-calibrated autonomy",
                core_argument=(
                    "Agent autonomy should depend on decision risk "
                    "and reversibility."
                ),
                why_it_matters=(
                    "Different decisions justify different levels "
                    "of human control."
                ),
                supporting_evidence=[],
                counterargument=None,
                uncertainty=None,
                contribution=(
                    "Use risk and reversibility to define autonomy boundaries."
                ),
            ),
        ]
    )


def _build_test_graph():
    graph = StateGraph(LinkedInAgentState)

    graph.add_node(
        "human_perspective_selection",
        human_perspective_selection_node,
    )
    graph.set_entry_point("human_perspective_selection")
    graph.add_edge("human_perspective_selection", END)

    return graph.compile(
        checkpointer=InMemorySaver(),
    )


def test_human_perspective_selection_interrupts_and_resumes():
    graph = _build_test_graph()

    perspective_set = _make_perspective_set()

    config = {
        "configurable": {
            "thread_id": "hitl-perspective-selection-test",
        }
    }

    initial_state = {
        "perspective_set": perspective_set,
    }

    interrupted = graph.invoke(
        initial_state,
        config=config,
    )

    assert "__interrupt__" in interrupted

    interrupt_payload = interrupted["__interrupt__"][0].value

    assert interrupt_payload["type"] == "perspective_selection"
    assert [
        perspective["perspective_id"]
        for perspective in interrupt_payload["perspectives"]
    ] == [
        "operating-model",
        "risk-calibrated-autonomy",
    ]

    resumed = graph.invoke(
        Command(
            resume={
                "perspective_id": "risk-calibrated-autonomy",
                "human_guidance": (
                    "Connect this with practical operational decision making."
                ),
            }
        ),
        config=config,
    )

    selected = resumed["selected_perspective"]

    assert (
        selected.perspective.perspective_id
        == "risk-calibrated-autonomy"
    )
    assert selected.human_guidance == (
        "Connect this with practical operational decision making."
    )
