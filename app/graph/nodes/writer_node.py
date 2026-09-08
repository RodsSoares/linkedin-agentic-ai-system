from app.components.writer import writer
from app.graph.state import LinkedInAgentState
from app.schemas.writer import WriterInput


def writer_node(state: LinkedInAgentState) -> dict:
    post = state.get("post")

    if post is None:
        raise ValueError("Writer node requires a PostCandidate.")

    quality_evaluation = state.get("quality_evaluation")

    writer_input = WriterInput(
        post=post,
        research_result=state.get("research_result"),
        previous_draft=state.get("current_draft"),
        revision_instruction=(
            quality_evaluation.revision_instruction
            if quality_evaluation is not None
            else None
        ),
    )

    draft = writer(writer_input)

    return {
        "current_draft": draft,
        "iteration": state.get("iteration", 0) + 1,
        "next_step": "evaluator",
        "status": "DRAFT_READY",
    }
