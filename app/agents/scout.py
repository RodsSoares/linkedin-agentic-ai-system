from datetime import datetime
from time import perf_counter
from typing import Any, Callable
from contextvars import ContextVar

from openai import OpenAI

from app.config.settings import (
    MODEL_NAME,
    OPENAI_API_KEY,
    SCOUT_READ_CONTEXT_MAX_TOKENS,
)
from app.context_preparation import prepare_context
from app.memory.service import InteractionMemoryService
from app.schemas.post import PostCandidate
from app.schemas.scout import ScoutAction, ScoutState
from app.schemas.tools import ReadTool, SearchResult, SearchTool
from app.tools.errors import WebToolError
from app.telemetry.usage import record_context_usage, record_openai_usage


client = OpenAI(api_key=OPENAI_API_KEY)


ScoutObserver = Callable[[str, dict[str, Any]], None]


_SCOUT_OBSERVER: ContextVar[ScoutObserver | None] = ContextVar(
    "scout_observer",
    default=None,
)


def set_scout_observer(observer: ScoutObserver | None):
    return _SCOUT_OBSERVER.set(observer)


def reset_scout_observer(token) -> None:
    _SCOUT_OBSERVER.reset(token)


def _log(message: str) -> None:
    """Emit concise operational telemetry to the VS Code terminal."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [SCOUT] {message}", flush=True)


def _observe(
    observer: ScoutObserver | None,
    event: str,
    state: ScoutState,
    **details: Any,
) -> None:
    if observer is None:
        return
    payload = {
        "event": event,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "state": {
            "status": state.status,
            "steps": state.steps,
            "max_steps": state.max_steps,
            "searches": len(state.search_queries),
            "visited_urls": len(state.visited_urls),
            "candidates": len(state.candidates),
            "search_results": len(state.search_results),
            "novelty_search_attempts": state.novelty_search_attempts,
            "max_novelty_search_attempts": state.max_novelty_search_attempts,
            "last_search_outcome": state.last_search_outcome,
            "last_read_url": state.last_read_url,
            "last_error": state.last_error,
            "max_searches": state.max_searches,
            "read_attempts": state.read_attempts,
            "max_reads": state.max_reads,
            "successful_reads": state.successful_reads,
            "blocked_reads": state.blocked_reads,
            "sources_discovered": state.sources_discovered,
            "already_seen": state.already_seen,
            "diversification_count": state.diversification_count,
            "search_strategy": state.search_strategy,
        },
        "details": details,
    }
    observer(event, payload)


SCOUT_SYSTEM_PROMPT = """
You are the Scout Agent.

Your objective is to discover potentially valuable content for professional
interaction.

You operate inside a bounded environment.

You may choose exactly one action at a time:

SEARCH:
Use when you need to discover content.
Provide a search query.

READ:
Use when a previously discovered result appears worth inspecting.
Provide its URL.

SELECT:
Use when the content you most recently read is valuable enough to become
a candidate for further opportunity evaluation.
Provide a selection reason.

FINISH:
Use when enough useful candidates have been found or further exploration
is unlikely to add value.

Rules:
- Do not invent URLs.
- Do not repeat searches unnecessarily.
- Do not revisit URLs already inspected.
- Only SELECT content that has already been read.
- Prefer actions that contribute directly to the objective.
- You do not publish, comment, or contact anyone.
- Return exactly one structured ScoutAction.
- If last_search_outcome is NO_NOVEL_RESULTS, the search worked but every
  discovered URL was already known from previous runs. Reformulate the search
  query semantically instead of repeating the same strategy.
- If last_search_outcome is NO_SEARCH_RESULTS, the search returned no results.
- Novelty retries are bounded. Do not attempt to bypass operational limits.
- When novelty is low or a source cannot be read, explore a materially different
  query or another discovered source instead of repeating a blocked URL.
- Diversify among governance, business operations, technical implementation,
  counterarguments, and current practical applications when relevant to the objective.
- A failed READ does not imply that the topic lacks worthwhile content.
""".strip()


def decide_next_action(state: ScoutState) -> ScoutAction:
    started_at = perf_counter()
    _log(f"LLM decision START | step={state.steps + 1}/{state.max_steps}")
    response = client.responses.parse(
        model=MODEL_NAME,
        instructions=SCOUT_SYSTEM_PROMPT,
        input=state.model_dump_json(indent=2),
        text_format=ScoutAction,
    )
    record_openai_usage(
        component="scout",
        operation="decide_next_action",
        model=MODEL_NAME,
        response=response,
        latency_ms=(perf_counter() - started_at) * 1000,
    )

    action = response.output_parsed
    elapsed = perf_counter() - started_at

    if action is None:
        _log(f"LLM decision ERROR | no structured action | {elapsed:.1f}s")
        raise RuntimeError(
            "Scout returned no structured action."
        )

    _log(f"LLM decision COMPLETE | action={action.action} | {elapsed:.1f}s")
    return action


def _filter_novel_search_results(
    results: list[SearchResult],
    memory_service: InteractionMemoryService,
) -> list[SearchResult]:
    unseen_urls = memory_service.filter_unseen_urls(
        [result.url for result in results]
    )

    results_by_url = {
        result.url: result
        for result in results
    }

    return [
        results_by_url[url]
        for url in unseen_urls
        if url in results_by_url
    ]


def execute_action(
    action: ScoutAction,
    state: ScoutState,
    search_tool: SearchTool,
    read_tool: ReadTool,
    memory_service: InteractionMemoryService | None = None,
    observer: ScoutObserver | None = None,
) -> str | list[SearchResult] | None:

    if state.steps >= state.max_steps:
        state.status = "FINISHED"
        return None

    if action.action == "SEARCH":
        if len(state.search_queries) >= state.max_searches:
            raise ValueError("Scout search budget exhausted.")
        if not action.query:
            raise ValueError(
                "SEARCH action requires a query."
            )

        if action.query.strip().casefold() in {
            query.strip().casefold() for query in state.search_queries
        }:
            raise ValueError(
                "Scout attempted to repeat a search query."
            )

        state.status = "SEARCHING"
        state.search_queries.append(action.query)
        _observe(observer, "search_started", state, query=action.query)

        tool_started = perf_counter()
        _log(f"SEARCH START | query={action.query!r}")
        results = search_tool(action.query)
        search_count = len(results) if results else 0
        state.sources_discovered += search_count
        _log(
            f"SEARCH COMPLETE | results={search_count} | "
            f"{perf_counter() - tool_started:.1f}s"
        )
        _observe(observer, "search_completed", state, query=action.query, results=search_count)

        if not results:
            state.search_results = []
            state.last_search_outcome = "NO_SEARCH_RESULTS"
            return []

        if memory_service is None:
            state.search_results = results
            state.last_search_outcome = "HAS_NOVEL_RESULTS"
            state.novelty_search_attempts = 0
            return results

        novel_results = _filter_novel_search_results(
            results=results,
            memory_service=memory_service,
        )
        state.already_seen += len(results) - len(novel_results)
        _log(
            f"NOVELTY FILTER | novel={len(novel_results)}/{len(results)} | "
            f"attempt={state.novelty_search_attempts + 1}"
        )
        _observe(
            observer,
            "novelty_filtered",
            state,
            novel=len(novel_results),
            total=len(results),
        )

        if not novel_results:
            state.search_results = []
            state.last_search_outcome = "NO_NOVEL_RESULTS"
            state.novelty_search_attempts += 1

            if (
                state.novelty_search_attempts
                >= state.max_novelty_search_attempts
            ):
                state.diversification_count += 1
                state.search_strategy = "diversify"
                state.novelty_search_attempts = 0
                _observe(observer, "query_diversification_required", state)

            return []

        state.search_results = novel_results
        state.last_search_outcome = "HAS_NOVEL_RESULTS"
        state.novelty_search_attempts = 0

        return novel_results

    if action.action == "READ":
        if state.read_attempts >= state.max_reads:
            raise ValueError("Scout read budget exhausted.")
        if not action.url:
            raise ValueError(
                "READ action requires a URL."
            )

        discovered_urls = {
            result.url
            for result in state.search_results
        }

        if action.url not in discovered_urls:
            raise ValueError(
                "Scout attempted to read a URL that was not discovered."
            )

        if action.url in state.blocked_urls:
            raise ValueError("Scout attempted to revisit a blocked URL.")

        if action.url in state.visited_urls:
            raise ValueError(
                "Scout attempted to revisit a URL."
            )

        result = next(
            result
            for result in state.search_results
            if result.url == action.url
        )

        state.status = "READING"
        state.last_read_url = None
        state.last_read_content = None
        state.read_attempts += 1

        tool_started = perf_counter()
        _observe(observer, "read_started", state, url=result.url)
        _log(f"READ START | url={result.url}")
        try:
            raw_content = read_tool(result.url)
        except WebToolError as error:
            state.blocked_reads += 1
            state.blocked_urls.append(result.url)
            _observe(observer, "read_blocked", state, url=result.url, error=str(error))
            raise
        read_elapsed = perf_counter() - tool_started
        _log(f"READ COMPLETE | {read_elapsed:.1f}s")
        _observe(observer, "read_completed", state, url=result.url)

        prepared = prepare_context(
            raw_content,
            max_tokens=SCOUT_READ_CONTEXT_MAX_TOKENS,
        )
        record_context_usage(
            component="scout",
            operation="read_context",
            original_tokens=prepared.original_tokens,
            prepared_tokens=prepared.prepared_tokens,
            truncated=prepared.truncated,
        )

        _log(
            "CONTEXT PREPARED | "
            f"tokens={prepared.prepared_tokens} | truncated={prepared.truncated}"
        )

        state.last_read_url = result.url
        state.last_read_content = prepared.content

        # A URL only becomes visited after a successful READ and
        # successful context preparation.
        state.visited_urls.append(result.url)
        state.successful_reads += 1

        if memory_service is not None:
            memory_service.record_visit(result.url)

        return prepared.content

    if action.action == "SELECT":
        if not state.last_read_url:
            raise ValueError(
                "Scout attempted to select content without reading it first."
            )

        if not state.last_read_content:
            raise ValueError(
                "Scout attempted to select empty content."
            )

        if not action.selection:
            raise ValueError(
                "SELECT action requires a selection."
            )

        result = next(
            result
            for result in state.search_results
            if result.url == state.last_read_url
        )

        already_selected = any(
            candidate.post_id == result.url
            or candidate.post_url == result.url
            for candidate in state.candidates
        )

        if already_selected:
            return None

        candidate = PostCandidate(
            post_id=result.url,
            author_name="Unknown",
            post_text=state.last_read_content,
            post_url=result.url,
        )

        state.candidates.append(candidate)
        state.status = "FINISHED"
        _log(f"SELECT | candidate={result.url}")
        _observe(observer, "candidate_selected", state, url=result.url)

        if memory_service is not None:
            memory_service.mark_selected(result.url)

        return None

    if action.action == "FINISH":
        state.status = "FINISHED"
        _log("FINISH action received")
        _observe(observer, "finish", state)
        return None

    raise ValueError(
        f"Unsupported Scout action: {action.action}"
    )


def run_scout(
    objective: str,
    search_tool: SearchTool,
    read_tool: ReadTool,
    max_steps: int = 24,
    max_novelty_search_attempts: int = 3,
    memory_service: InteractionMemoryService | None = None,
    observer: ScoutObserver | None = None,
    max_searches: int = 8,
    max_reads: int = 8,
) -> ScoutState:
    observer = observer or _SCOUT_OBSERVER.get()

    state = ScoutState(
        objective=objective,
        max_steps=max_steps,
        max_novelty_search_attempts=max_novelty_search_attempts,
        max_searches=max_searches,
        max_reads=max_reads,
    )

    run_started = perf_counter()
    _log(
        f"START | max_steps={max_steps} | "
        f"max_novelty_attempts={max_novelty_search_attempts}"
    )
    _observe(observer, "scout_started", state)

    while state.status != "FINISHED":
        if state.steps >= state.max_steps:
            state.status = "FINISHED"
            break

        if (
            len(state.search_queries) >= state.max_searches
            and state.read_attempts >= state.max_reads
            and not state.last_read_url
        ):
            state.status = "FINISHED"
            _observe(observer, "budgets_exhausted", state)
            break

        _observe(observer, "llm_decision_started", state)
        action = decide_next_action(state)
        _observe(
            observer,
            "llm_decision_completed",
            state,
            action=action.action,
            query=action.query,
            url=action.url,
        )

        try:
            execute_action(
                action=action,
                state=state,
                search_tool=search_tool,
                read_tool=read_tool,
                memory_service=memory_service,
                observer=observer,
            )
            state.last_error = None

        except ValueError as error:
            state.last_error = str(error)
            _log(f"STEP ERROR | ValueError: {error}")
            _observe(observer, "recoverable_error", state, error=str(error))

        except WebToolError as error:
            state.last_error = f"Web tool failure: {error}"
            _log(f"STEP ERROR | WebToolError: {error}")
            _observe(observer, "recoverable_error", state, error=str(error))

        state.steps += 1
        _log(
            f"STEP COMPLETE | step={state.steps}/{state.max_steps} | "
            f"status={state.status} | candidates={len(state.candidates)}"
        )
        _observe(observer, "step_completed", state)

    _observe(observer, "scout_completed", state)
    _log(
        f"COMPLETE | steps={state.steps} | candidates={len(state.candidates)} | "
        f"{perf_counter() - run_started:.1f}s"
    )
    return state
