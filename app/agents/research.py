from collections.abc import Callable

from app.config.settings import (
    RESEARCH_READ_CONTEXT_MAX_TOKENS,
    RESEARCH_TOTAL_READ_CONTEXT_MAX_TOKENS,
)
from app.context_preparation import count_tokens, prepare_context
from app.schemas.research import (
    ReadSource,
    ResearchAction,
    ResearchActionType,
    ResearchBrief,
    ResearchBriefSynthesis,
    ResearchObjective,
    ResearchState,
    ResearchStatus,
)
from app.schemas.tools import ReadTool, SearchResult, SearchTool
from app.tools.errors import WebToolError


MAX_RESEARCH_STEPS = 10
MAX_RESEARCH_DECISIONS = 12
MAX_RESEARCH_SEARCHES = 3
MAX_RESEARCH_READS = 5
MAX_RESEARCH_EVIDENCE_ITEMS = 6


ObjectiveBuilder = Callable[[ResearchState], ResearchObjective]
ActionDecider = Callable[[ResearchState], ResearchAction]
BriefBuilder = Callable[[ResearchState], ResearchBriefSynthesis]


def initialize_research_objective(
    state: ResearchState,
    objective_builder: ObjectiveBuilder,
) -> ResearchState:
    if state.research_objective is not None:
        return state

    state.research_objective = objective_builder(state)

    return state


def run_research_loop(
    state: ResearchState,
    objective_builder: ObjectiveBuilder,
    action_decider: ActionDecider,
    search_tool: SearchTool,
    read_tool: ReadTool,
) -> ResearchState:
    state = initialize_research_objective(
        state=state,
        objective_builder=objective_builder,
    )

    while state.status is None:
        if state.decision_attempts >= MAX_RESEARCH_DECISIONS:
            state.status = ResearchStatus.LIMIT_REACHED
            state.last_error = "Maximum research decisions reached."
            break

        action = action_decider(state)
        state.decision_attempts += 1

        state = execute_research_action(
            state=state,
            action=action,
            search_tool=search_tool,
            read_tool=read_tool,
        )

    return state


def build_research_brief(
    state: ResearchState,
    brief_builder: BriefBuilder,
) -> ResearchBrief:
    if state.research_objective is None:
        raise ValueError(
            "ResearchBrief cannot be built without a ResearchObjective."
        )

    if state.status is None:
        raise ValueError(
            "ResearchBrief cannot be built from an unfinished ResearchState."
        )

    synthesis = brief_builder(state)

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


def execute_research_action(
    state: ResearchState,
    action: ResearchAction,
    search_tool: SearchTool,
    read_tool: ReadTool,
) -> ResearchState:
    if state.steps >= MAX_RESEARCH_STEPS:
        state.status = ResearchStatus.LIMIT_REACHED
        state.last_error = "Maximum research steps reached."
        return state

    if action.action == ResearchActionType.SEARCH:
        return _execute_search(
            state=state,
            action=action,
            search_tool=search_tool,
        )

    if action.action == ResearchActionType.READ:
        return _execute_read(
            state=state,
            action=action,
            read_tool=read_tool,
        )

    if action.action == ResearchActionType.EXTRACT:
        return _execute_extract(
            state=state,
            action=action,
        )

    if action.action == ResearchActionType.FINISH:
        return _execute_finish(
            state=state,
            action=action,
        )

    state.last_error = f"Unsupported research action: {action.action}"
    return state


def _execute_search(
    state: ResearchState,
    action: ResearchAction,
    search_tool: SearchTool,
) -> ResearchState:
    query = action.search_query

    if query is None or not query.strip():
        state.last_error = "SEARCH requires a non-empty search query."
        return state

    if query in state.search_queries:
        state.last_error = "Search query has already been executed."
        return state

    if state.search_count >= MAX_RESEARCH_SEARCHES:
        state.last_error = (
            "Maximum research searches reached. "
            "Choose another valid action."
        )
        return state

    state.search_queries.append(query)
    state.search_count += 1
    state.steps += 1

    try:
        results = search_tool(query)
    except WebToolError as error:
        state.last_error = f"Web search failed: {error}"
        return state

    known_urls = {result.url for result in state.search_results}
    unique_results = [
        result
        for result in results
        if result.url not in known_urls
    ]

    state.search_results.extend(unique_results)
    state.last_error = None

    return state


def _current_read_context_tokens(state: ResearchState) -> int:
    return sum(
        count_tokens(read_source.content)
        for read_source in state.read_sources
    )


def _execute_read(
    state: ResearchState,
    action: ResearchAction,
    read_tool: ReadTool,
) -> ResearchState:
    url = action.url

    if url is None or not url.strip():
        state.last_error = "READ requires a URL."
        return state

    discovered_result = next(
        (
            result
            for result in state.search_results
            if result.url == url
        ),
        None,
    )

    if discovered_result is None:
        state.last_error = "READ URL was not discovered by SEARCH."
        return state

    if url in state.visited_urls:
        state.last_error = "URL has already been read."
        return state

    if state.read_count >= MAX_RESEARCH_READS:
        state.last_error = (
            "Maximum research reads reached. "
            "Choose another valid action."
        )
        return state

    used_context_tokens = _current_read_context_tokens(state)
    remaining_context_tokens = (
        RESEARCH_TOTAL_READ_CONTEXT_MAX_TOKENS
        - used_context_tokens
    )

    if remaining_context_tokens <= 0:
        state.last_error = (
            "Research read-context token budget is exhausted. "
            "Choose EXTRACT or FINISH."
        )
        return state

    state.visited_urls.append(url)
    state.read_count += 1
    state.steps += 1

    try:
        raw_content = read_tool(url)
    except WebToolError as error:
        state.last_error = (
            f"Web read failed for {url}: {error}"
        )
        return state

    per_read_budget = min(
        RESEARCH_READ_CONTEXT_MAX_TOKENS,
        remaining_context_tokens,
    )

    prepared = prepare_context(
        raw_content,
        max_tokens=per_read_budget,
    )

    state.read_sources.append(
        ReadSource(
            url=url,
            title=discovered_result.title,
            content=prepared.content,
        )
    )

    state.last_error = None

    return state


def _execute_extract(
    state: ResearchState,
    action: ResearchAction,
) -> ResearchState:
    evidence = action.evidence

    if evidence is None:
        state.last_error = "EXTRACT requires an EvidenceItem."
        return state

    source = next(
        (
            read_source
            for read_source in state.read_sources
            if read_source.url == evidence.source_url
        ),
        None,
    )

    if source is None:
        state.last_error = "Evidence source has not been read."
        return state

    if source.title != evidence.source_title:
        state.last_error = "Evidence source title does not match the read source."
        return state

    if evidence in state.evidence:
        state.last_error = "Evidence item has already been extracted."
        return state

    if len(state.evidence) >= MAX_RESEARCH_EVIDENCE_ITEMS:
        state.last_error = (
            "Maximum research evidence items reached. "
            "Choose another valid action."
        )
        return state

    state.evidence.append(evidence)
    state.steps += 1
    state.last_error = None

    return state


def _execute_finish(
    state: ResearchState,
    action: ResearchAction,
) -> ResearchState:
    finish_status = action.finish_status

    if finish_status is None:
        state.last_error = (
            "FINISH requires finish_status to be SUFFICIENT or INSUFFICIENT."
        )
        return state

    if finish_status == ResearchStatus.LIMIT_REACHED:
        state.last_error = (
            "FINISH cannot request LIMIT_REACHED. "
            "Operational limits are owned by the Python runtime."
        )
        return state

    if (
        finish_status == ResearchStatus.SUFFICIENT
        and not state.evidence
    ):
        state.last_error = (
            "FINISH cannot declare SUFFICIENT without extracted evidence."
        )
        return state

    state.status = finish_status
    state.steps += 1
    state.last_error = None

    return state
