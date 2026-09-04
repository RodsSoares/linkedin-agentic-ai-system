from app.schemas.evaluator import EvaluatorInput, QualityEvaluation


def evaluator(input_data: EvaluatorInput) -> QualityEvaluation:
    draft = input_data.current_draft

    if not draft.strip():
        return QualityEvaluation(
            factual_accuracy=0,
            relevance=0,
            voice_match=0,
            decision="REJECT",
            revision_instruction="The draft is empty.",
        )

    if "REVISADO" not in draft:
        return QualityEvaluation(
            factual_accuracy=100,
            relevance=100,
            voice_match=50,
            decision="REVISE",
            revision_instruction="Revise the draft to better match Rodrigo's voice.",
        )

    return QualityEvaluation(
        factual_accuracy=100,
        relevance=100,
        voice_match=100,
        decision="PASS",
        revision_instruction=None,
    )