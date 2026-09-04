from app.components.evaluator import evaluator
from app.graph.state import LinkedInAgentState
from app.schemas.evaluator import EvaluatorInput


def evaluator_node(state: LinkedInAgentState) -> dict:
    post = state["post"]
    current_draft = state["current_draft"]

    if post is None:
        raise ValueError("Evaluator node requires a PostCandidate.")

    if current_draft is None:
        raise ValueError("Evaluator node requires a current draft.")

    evaluator_input = EvaluatorInput(
        post=post,
        current_draft=current_draft,
        research_result=state["research_result"],
    )

    evaluation = evaluator(evaluator_input)

    return {
        "quality_evaluation": evaluation,
        "next_step": evaluation.decision,
        "status": "EVALUATED",
    }