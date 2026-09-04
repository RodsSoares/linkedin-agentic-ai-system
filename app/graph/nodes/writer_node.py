from app.components.writer import writer
from app.graph.state import LinkedInAgentState
from app.schemas.writer import WriterInput


def writer_node(state: LinkedInAgentState) -> dict:
    post = state["post"]

    if post is None:
        raise ValueError("Writer node requires a PostCandidate.")

    writer_input = WriterInput(
        post=post,
        research_result=state["research_result"],
        previous_draft=state["current_draft"],
        revision_instruction=(
            state["quality_evaluation"].revision_instruction
            if state["quality_evaluation"] is not None
            else None
        ),
    )

    draft = writer(writer_input)

    return {
        "current_draft": draft,
        "iteration": state["iteration"] + 1,
        "next_step": "evaluator",
        "status": "EVALUATING",
    }