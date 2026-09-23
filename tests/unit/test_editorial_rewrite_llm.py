from app.components.editorial_preference_semantic import (
    evaluate_editorial_preference_semantics,
)
from app.components.editorial_rewrite import (
    rewrite_with_editorial_preference,
)
from app.schemas.editorial_preference import EditorialPreferenceInput
from app.schemas.editorial_rewrite import EditorialRewriteInput
from app.schemas.scout import PostCandidate


SOURCE_POST = """
Antes de automatizar, eu gosto de entender o processo.

Por que ele existe?
Onde estão os gargalos?
O que poderia ser simplificado?
E, principalmente, qual resultado esperamos melhorar?

Nem toda transformação precisa começar com uma nova ferramenta.
Às vezes, precisa começar com uma nova pergunta.
""".strip()


AGENTIC_DRAFT = """
A pergunta mais importante talvez seja: qual etapa pode deixar de existir sem comprometer cliente, controle ou compliance? Depois vêm combinar, reordenar e simplificar.

Só então a automação faz sentido. E o resultado precisa aparecer no fluxo: menos tempo de atravessamento, menos retrabalho e maior qualidade na primeira execução — não apenas mais velocidade em uma etapa isolada.
""".strip()


# Intentionally excludes Rodrigo's published human final for this case.
CALIBRATION_CONTEXT = """
Observed Rodrigo Voice tendencies from prior calibration cases:

- Prefer one central professional contribution over several parallel insights.
- Preserve the strongest technical or operational thesis while removing secondary
  explanation once it stops increasing the contribution.
- Prefer concise, conversational professional participation over white-paper or
  consultant-style exposition.
- Use evidence selectively; available research does not need to be displayed
  exhaustively in the final comment.
- Favor practical process, business, architecture, or execution insight.
- Avoid generic LinkedIn polish, excessive rhetorical symmetry, and explanatory
  completeness for its own sake.
- Stop after the strongest useful point is clear.
- Do not reward brevity by itself: compression must preserve the useful thesis.
""".strip()


def main() -> None:
    source_post = PostCandidate(
        post_id=(
            "https://www.linkedin.com/feed/update/"
            "urn:li:activity:7503939501287952385/"
        ),
        author_name="Guilherme Juliani",
        post_text=SOURCE_POST,
        post_url=(
            "https://www.linkedin.com/feed/update/"
            "urn:li:activity:7503939501287952385/"
        ),
        source="target_url",
    )

    preference_input = EditorialPreferenceInput(
        source_post=source_post,
        research_result=None,
        draft=AGENTIC_DRAFT,
        content_intent="COMMENT",
        calibration_context=CALIBRATION_CONTEXT,
    )

    editorial_evaluation = evaluate_editorial_preference_semantics(
        preference_input
    )

    rewrite_input = EditorialRewriteInput(
        source_post=source_post,
        research_result=None,
        original_draft=AGENTIC_DRAFT,
        editorial_evaluation=editorial_evaluation,
        calibration_context=CALIBRATION_CONTEXT,
    )

    rewrite_result = rewrite_with_editorial_preference(rewrite_input)

    print("\n=== ORIGINAL AGENTIC DRAFT ===\n")
    print(AGENTIC_DRAFT)

    print("\n=== EDITORIAL PREFERENCE EVALUATION ===\n")
    print(editorial_evaluation.model_dump_json(indent=2))

    print("\n=== EDITORIAL REWRITE ===\n")
    print(rewrite_result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
