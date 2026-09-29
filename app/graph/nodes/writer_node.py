from app.components.writer import writer
from app.graph.state import LinkedInAgentState
from app.schemas.writer import WriterInput


def writer_node(state: LinkedInAgentState) -> dict:
    post = state.get("post")

    if post is None:
        raise ValueError("Writer node requires a PostCandidate.")

    quality_evaluation = state.get("quality_evaluation")
    final_refinement_action = state.get("final_refinement_action")
    final_refinement_guidance = state.get("final_refinement_guidance")

    is_final_refinement = final_refinement_action == "refine"

    writer_input = WriterInput(
        post=post,
        research_result=state.get("research_result"),
        selected_perspective=state.get("selected_perspective"),
        content_mode=state.get("content_mode") or "linkedin_reply",
        previous_draft=state.get("current_draft"),
        revision_instruction=(
            None
            if is_final_refinement
            else (
                quality_evaluation.revision_instruction
                if quality_evaluation is not None
                else None
            )
        ),
        final_refinement_guidance=(
            final_refinement_guidance
            if is_final_refinement
            else None
        ),
    )

    draft = writer(writer_input)

    return {
        "current_draft": draft,
        "iteration": state.get("iteration", 0) + 1,
        "next_step": (
            "final"
            if is_final_refinement
            else "evaluator"
        ),
        "status": (
            "FINAL_REFINEMENT_READY"
            if is_final_refinement
            else "DRAFT_READY"
        ),
    }
