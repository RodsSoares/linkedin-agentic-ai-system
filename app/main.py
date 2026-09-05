from app.graph.workflow import build_workflow
from app.schemas.post import PostCandidate


def main():
    workflow = build_workflow()

    post = PostCandidate(
        post_id="001",
        author_name="Teste",
        post_text="Inteligência artificial está transformando as operações.",
        post_url="https://linkedin.com/posts/001",
    )

    initial_state = {
        "post": post,
        "opportunity_score": None,
        "research_result": None,
        "current_draft": None,
        "quality_evaluation": None,
        "iteration": 0,
        "next_step": None,
        "human_feedback": None,
        "status": "STARTED",
    }

    final_state = workflow.invoke(initial_state)

    evaluation = final_state["quality_evaluation"]

    print("\n=== FINAL STATE ===")
    print(f"Status: {final_state['status']}")
    print(f"Iterations: {final_state['iteration']}")
    print(f"Draft: {final_state['current_draft']}")
    print(f"Factual accuracy: {evaluation.factual_accuracy}")
    print(f"Relevance: {evaluation.relevance}")
    print(f"Voice match: {evaluation.voice_match}")
    print(f"Decision: {evaluation.decision}")
    print(f"Revision instruction: {evaluation.revision_instruction}")


if __name__ == "__main__":
    main()