from app.components.editorial_rewrite import rewrite_with_editorial_preference
from app.schemas.editorial_preference import EditorialPreferenceEvaluation
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


# Frozen from the earlier real Editorial Preference run.
# This isolates the Rewrite capability from evaluator variance.
#
# The original frozen evaluation used the older v0.1 schema
# (preserve_elements / unnecessary_elements). The semantic judgment below is
# preserved while being represented through the current v0.2.2 schema.
FROZEN_EDITORIAL_EVALUATION = EditorialPreferenceEvaluation(
    central_thesis_focus=92,
    contribution_density=88,
    conversational_naturalness=82,
    selective_evidence_use=100,
    stopping_discipline=86,
    front_loaded_value=70,
    synthetic_completeness_risk=36,
    publication_likelihood=78,
    core_thesis=(
        "Antes de automatizar, é preciso avaliar se o processo ou alguma de suas "
        "etapas deveria continuar existindo como está."
    ),
    must_preserve_elements=[
        (
            "Questionar se partes do processo precisam existir antes de "
            "automatizá-las."
        ),
    ],
    optional_support_elements=[
        (
            "A pergunta operacional sobre eliminar uma etapa sem comprometer "
            "cliente, controle ou compliance."
        ),
        (
            "A tese de que automação só deve vir depois de repensar e "
            "simplificar o fluxo."
        ),
        (
            "O critério de avaliar o resultado no fluxo inteiro, e não pela "
            "velocidade de uma etapa isolada."
        ),
    ],
    remove_or_compress_elements=[
        (
            "A sequência “combinar, reordenar e simplificar” acrescenta uma "
            "segunda enumeração de ações depois de a pergunta sobre eliminar "
            "etapas já ter estabelecido o ponto central."
        ),
        (
            "A lista final “menos tempo de atravessamento, menos retrabalho e "
            "maior qualidade na primeira execução” é útil, mas tem um acabamento "
            "simétrico que poderia ser ligeiramente comprimido se não houver "
            "espaço para detalhá-la no contexto da discussão."
        ),
    ],
    editorial_reason=(
        "O comentário acrescenta uma contribuição operacional clara e diretamente "
        "conectada ao post: antes de automatizar, vale questionar se partes do "
        "processo precisam existir. Mantém um foco dominante e fecha com um critério "
        "de resultado relevante. Há apenas um leve excesso de enumerações, que deixa "
        "o texto um pouco mais polido e completo do que o necessário, sem comprometer "
        "sua utilidade."
    ),
    decision="PASS",
)


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

    rewrite_input = EditorialRewriteInput(
        source_post=source_post,
        research_result=None,
        original_draft=AGENTIC_DRAFT,
        editorial_evaluation=FROZEN_EDITORIAL_EVALUATION,
        calibration_context=CALIBRATION_CONTEXT,
    )

    result = rewrite_with_editorial_preference(rewrite_input)

    print("\n=== ORIGINAL AGENTIC DRAFT (A) ===\n")
    print(AGENTIC_DRAFT)

    print("\n=== FROZEN EDITORIAL EVALUATION ===\n")
    print(FROZEN_EDITORIAL_EVALUATION.model_dump_json(indent=2))

    print("\n=== EDITORIAL REWRITE (B) ===\n")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()