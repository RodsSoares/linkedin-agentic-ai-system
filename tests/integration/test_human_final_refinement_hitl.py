from unittest.mock import patch

from app.graph.nodes.writer_node import writer_node
from app.graph.routing import (
    route_after_final_refinement,
    route_after_writer,
)
from app.schemas.post import PostCandidate


from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import Command

from app.graph.nodes.human_final_refinement_node import (
    human_final_refinement_node,
)
from app.graph.state import LinkedInAgentState
from app.schemas.evaluator import QualityEvaluation


def _build_test_graph():
    graph = StateGraph(LinkedInAgentState)

    graph.add_node(
        "human_final_refinement",
        human_final_refinement_node,
    )
    graph.set_entry_point("human_final_refinement")
    graph.add_edge("human_final_refinement", END)

    return graph.compile(
        checkpointer=InMemorySaver(),
    )


def _build_refinement_test_graph():
    graph = StateGraph(LinkedInAgentState)

    graph.add_node(
        "human_final_refinement",
        human_final_refinement_node,
    )
    graph.add_node(
        "writer",
        writer_node,
    )

    graph.set_entry_point("human_final_refinement")

    graph.add_conditional_edges(
        "human_final_refinement",
        route_after_final_refinement,
        {
            "writer": "writer",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "writer",
        route_after_writer,
        {
            "evaluator": "unexpected_evaluator",
            "end": END,
        },
    )

    def unexpected_evaluator(state):
        raise AssertionError(
            "Final human refinement must not return to evaluator."
        )

    graph.add_node(
        "unexpected_evaluator",
        unexpected_evaluator,
    )

    return graph.compile(
        checkpointer=InMemorySaver(),
    )


def test_human_final_refinement_interrupts_and_accepts():
    graph = _build_test_graph()

    original_draft = (
        "AI governance becomes operational only when "
        "decision boundaries are explicit."
    )

    config = {
        "configurable": {
            "thread_id": "hitl-final-refinement-accept-test",
        }
    }

    initial_state = {
        "current_draft": original_draft,
        "quality_evaluation": QualityEvaluation(
            factual_accuracy=95,
            relevance=95,
            voice_match=95,
            decision="PASS",
            revision_instruction=None,
        ),
    }

    interrupted = graph.invoke(
        initial_state,
        config=config,
    )

    assert "__interrupt__" in interrupted

    interrupt_payload = interrupted["__interrupt__"][0].value

    assert interrupt_payload["type"] == "final_refinement"
    assert interrupt_payload["current_draft"] == original_draft
    assert interrupt_payload["allowed_actions"] == [
        "accept",
        "refine",
    ]
    assert interrupt_payload["refinement_dimensions"] == [
        "tone",
        "emphasis",
        "length",
        "framing",
        "closing",
    ]

    resumed = graph.invoke(
        Command(
            resume={
                "action": "accept",
            }
        ),
        config=config,
    )

    assert resumed["final_refinement_action"] == "accept"
    assert resumed["final_refinement_guidance"] is None
    assert resumed["current_draft"] == original_draft


def test_human_final_refinement_refines_once_and_ends():
    graph = _build_refinement_test_graph()

    original_draft = (
        "AI governance becomes operational only when "
        "decision boundaries are explicit."
    )

    final_guidance = (
        "Make the closing more concise and decisive."
    )

    old_revision_instruction = (
        "Old evaluator instruction that must not leak."
    )

    config = {
        "configurable": {
            "thread_id": "hitl-final-refinement-refine-test",
        }
    }

    initial_state = {
        "post": PostCandidate(
            post_id="test-post-001",
            author_name="Test Author",
            post_text="Test source content.",
            post_url="https://example.com/post",
        ),
        "content_mode": "linkedin_post",
        "current_draft": original_draft,
        "quality_evaluation": QualityEvaluation(
            factual_accuracy=95,
            relevance=95,
            voice_match=95,
            decision="PASS",
            revision_instruction=old_revision_instruction,
        ),
        "iteration": 1,
    }

    with patch(
        "app.graph.nodes.writer_node.writer",
        return_value="Human-refined final draft.",
    ) as writer_mock:
        interrupted = graph.invoke(
            initial_state,
            config=config,
        )

        assert "__interrupt__" in interrupted

        resumed = graph.invoke(
            Command(
                resume={
                    "action": "refine",
                    "guidance": final_guidance,
                }
            ),
            config=config,
        )

    writer_mock.assert_called_once()

    writer_input = writer_mock.call_args.args[0]

    assert writer_input.previous_draft == original_draft
    assert writer_input.content_mode == "linkedin_post"

    assert writer_input.revision_instruction is None
    assert (
        writer_input.final_refinement_guidance
        == final_guidance
    )

    assert resumed["current_draft"] == (
        "Human-refined final draft."
    )
    assert resumed["final_refinement_action"] == "refine"
    assert resumed["final_refinement_guidance"] == final_guidance

    assert resumed["next_step"] == "final"
    assert resumed["status"] == "FINAL_REFINEMENT_READY"
