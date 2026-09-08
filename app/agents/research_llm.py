from typing import Any, TypeVar

from app.config.settings import MODEL_NAME
from app.schemas.research import (
    ResearchAction,
    ResearchBrief,
    ResearchBriefSynthesis,
    ResearchObjective,
    ResearchState,
)


T = TypeVar("T")


def build_research_objective_with_llm(
    state: ResearchState,
    llm: Any,
) -> ResearchObjective:
    prompt = _build_research_objective_prompt(state)

    return _parse_structured_response(
        llm=llm,
        prompt=prompt,
        output_model=ResearchObjective,
    )


def decide_research_action_with_llm(
    state: ResearchState,
    llm: Any,
) -> ResearchAction:
    prompt = _build_research_action_prompt(state)

    return _parse_structured_response(
        llm=llm,
        prompt=prompt,
        output_model=ResearchAction,
    )


def build_research_brief_with_llm(
    state: ResearchState,
    llm: Any,
) -> ResearchBrief:
    if state.research_objective is None:
        raise ValueError(
            "ResearchBrief cannot be built without a ResearchObjective."
        )

    if state.status is None:
        raise ValueError(
            "ResearchBrief cannot be built from an unfinished ResearchState."
        )

    prompt = _build_research_brief_prompt(state)

    synthesis = _parse_structured_response(
        llm=llm,
        prompt=prompt,
        output_model=ResearchBriefSynthesis,
    )

    return ResearchBrief(
        research_objective=state.research_objective,
        summary=synthesis.summary,
        key_findings=synthesis.key_findings,
        evidence=state.evidence,
        counterpoints=synthesis.counterpoints,
        unresolved_questions=synthesis.unresolved_questions,
        sources=state.search_results,
        status=state.status,
    )


def _parse_structured_response(
    llm: Any,
    prompt: str,
    output_model: type[T],
) -> T:
    response = llm.responses.parse(
        model=MODEL_NAME,
        input=prompt,
        text_format=output_model,
    )

    parsed = response.output_parsed

    if parsed is None:
        raise RuntimeError(
            f"OpenAI returned no parsed {output_model.__name__}."
        )

    return parsed


def _build_research_objective_prompt(
    state: ResearchState,
) -> str:
    return f"""
You are defining the bounded research objective for an approved LinkedIn
opportunity.

Your responsibility is to define the narrowest useful research objective
needed for the Writer to produce one relevant, factual, and defensible
LinkedIn contribution.

This is minimum-sufficient research, not exhaustive topic research.

Scope rules:
- define exactly one primary research question;
- use only 1 to 3 focus areas;
- keep each focus area directly tied to the specific contribution opportunity;
- prefer a question that can be answered with a small number of credible
  evidence items;
- do not expand into a broad market report, literature review, implementation
  guide, or complete survey of the topic.

Do not write the final LinkedIn contribution.
Do not decide whether the opportunity should be pursued.
Do not invent facts.

POST CANDIDATE:
{state.post.model_dump_json(indent=2)}

OPPORTUNITY EVALUATION:
{state.opportunity_evaluation.model_dump_json(indent=2)}

Return a ResearchObjective containing:
- exactly one narrow primary research question;
- between 1 and 3 focused areas that are directly useful for this opportunity.
""".strip()


def _build_research_action_prompt(
    state: ResearchState,
) -> str:
    objective = (
        state.research_objective.model_dump_json(indent=2)
        if state.research_objective is not None
        else "null"
    )

    search_queries = (
        "\n".join(f"- {query}" for query in state.search_queries)
        if state.search_queries
        else "None"
    )

    search_results = (
        "\n\n".join(
            result.model_dump_json(indent=2)
            for result in state.search_results
        )
        if state.search_results
        else "None"
    )

    read_sources = (
        "\n\n".join(
            source.model_dump_json(indent=2)
            for source in state.read_sources
        )
        if state.read_sources
        else "None"
    )

    evidence = (
        "\n\n".join(
            item.model_dump_json(indent=2)
            for item in state.evidence
        )
        if state.evidence
        else "None"
    )

    return f"""
You are controlling one bounded step of a Research capability.

Choose exactly one next action:
- SEARCH: discover potentially useful sources;
- READ: read a URL that was previously discovered by SEARCH;
- EXTRACT: record one evidence item from a source that has already been read;
- FINISH: stop when the narrow ResearchObjective has been sufficiently
  supported, or when further bounded work is unlikely to resolve an important
  evidence gap.

The Python runtime owns authorization, budgets, limits, and guardrails.
You only choose the semantically appropriate next action.

Important rules:
- SEARCH should use a useful, non-repeated query.
- READ may only request a URL already present in search results.
- EXTRACT may only cite a source already present in read sources.
- Do not invent source URLs, titles, or factual evidence.
- If LAST ERROR is present, correct the previous invalid action.
- Prefer the minimum amount of research necessary.
- Do not write the final LinkedIn contribution.

Research progression policy:
- SEARCH exists to discover candidate sources, not to accumulate queries.
- If there is a plausibly relevant discovered result that has not been read,
  prefer READ before another SEARCH.
- If a read source contains useful support that has not yet been captured,
  prefer EXTRACT before another SEARCH or READ.
- Use another SEARCH only when the currently discovered/read material cannot
  address an important gap in the narrow research objective.
- Once the evidence is sufficient for one defensible LinkedIn contribution,
  choose FINISH rather than broadening the research.
- FINISH requires finish_status:
  - SUFFICIENT only when the collected evidence is enough to support the narrow
    ResearchObjective without requiring unsupported claims;
  - INSUFFICIENT when useful evidence exists but an important part of the
    ResearchObjective remains unsupported, or when available sources do not
    justify the intended claim.
- Partial evidence is not the same as sufficient evidence.
- Never request LIMIT_REACHED in finish_status. LIMIT_REACHED is owned by the
  Python runtime and is reserved for operational budget/limit exhaustion.
- A local action-limit error means that action is unavailable; recover by
  choosing another valid action when useful work remains.
- When proposing an EvidenceItem:
  - relevance must be an integer from 0 to 100, where 0 means irrelevant and
    100 means maximally relevant to the ResearchObjective;
  - confidence must be an integer from 0 to 100, where 0 means unsupported and
    100 means very strongly supported by the observed source.

RESEARCH OBJECTIVE:
{objective}

SEARCH QUERIES ALREADY USED:
{search_queries}

SEARCH RESULTS DISCOVERED:
{search_results}

SOURCES ALREADY READ:
{read_sources}

EVIDENCE ALREADY EXTRACTED:
{evidence}

CURRENT COUNTERS:
steps={state.steps}
decision_attempts={state.decision_attempts}
search_count={state.search_count}
read_count={state.read_count}

LAST ERROR:
{state.last_error or "None"}

CURRENT STATUS:
{state.status.value if state.status is not None else "RUNNING"}

Return one ResearchAction.
For FINISH, populate finish_status with SUFFICIENT or INSUFFICIENT.
For non-FINISH actions, leave finish_status null.
""".strip()


def _build_research_brief_prompt(
    state: ResearchState,
) -> str:
    assert state.research_objective is not None
    assert state.status is not None

    evidence = (
        "\n\n".join(
            item.model_dump_json(indent=2)
            for item in state.evidence
        )
        if state.evidence
        else "None"
    )

    return f"""
You are producing the semantic synthesis for the final ResearchBrief.

The evidence boundary is strict:
- only extracted EvidenceItem objects may support factual findings;
- raw read-source content is operational research context, not validated evidence;
- search-result snippets are discovery metadata, not validated evidence;
- do not infer factual findings from sources that were read but not promoted
  through EXTRACT into EvidenceItem;
- if no EvidenceItem exists, explicitly state that the bounded research did not
  produce validated evidence sufficient to support factual findings.

Preserve uncertainty explicitly.
Counterpoints should capture meaningful limitations of the extracted evidence.
Unresolved questions should identify claims the Writer should avoid stating
strongly without additional evidence.

RESEARCH OBJECTIVE:
{state.research_objective.model_dump_json(indent=2)}

TERMINAL STATUS:
{state.status.value}

EXTRACTED EVIDENCE ONLY:
{evidence}

Return only a ResearchBriefSynthesis containing:
- summary;
- key_findings;
- counterpoints;
- unresolved_questions.

Do not return or rewrite research_objective, evidence, sources, or status.
Those fields are owned by the Python runtime and will be copied directly
from the terminal ResearchState into the final ResearchBrief.
""".strip()
