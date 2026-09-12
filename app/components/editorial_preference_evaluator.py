from collections.abc import Callable

from app.schemas.editorial_preference import (
    EditorialPreferenceEvaluation,
    EditorialPreferenceInput,
)


EditorialPreferenceSemanticEvaluator = Callable[
    [EditorialPreferenceInput],
    EditorialPreferenceEvaluation,
]


def evaluate_editorial_preference(
    evaluation_input: EditorialPreferenceInput,
    *,
    semantic_evaluator: EditorialPreferenceSemanticEvaluator,
) -> EditorialPreferenceEvaluation:
    """
    Execute one bounded semantic Editorial Preference evaluation.

    This component is intentionally isolated from workflow routing.

    Ownership:
    - The semantic evaluator interprets editorial fit.
    - Pydantic validates the structured result.
    - This function does not rewrite content, rerun Research, mutate state,
      route the graph, or make publication decisions.
    """
    result = semantic_evaluator(evaluation_input)

    if isinstance(result, EditorialPreferenceEvaluation):
        return result

    return EditorialPreferenceEvaluation.model_validate(result)
