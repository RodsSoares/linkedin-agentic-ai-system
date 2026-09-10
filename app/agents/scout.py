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


client = OpenAI(api_key=OPENAI_API_KEY)


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
""".strip()


def decide_next_action(state: ScoutState) -> ScoutAction:
    response = client.responses.parse(
        model=MODEL_NAME,
        instructions=SCOUT_SYSTEM_PROMPT,
        input=state.model_dump_json(indent=2),
        text_format=ScoutAction,
    )

    action = response.output_parsed

    if action is None:
        raise RuntimeError(
            "Scout returned no structured action."
        )

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
) -> str | list[SearchResult] | None:

    if state.steps >= state.max_steps:
        state.status = "FINISHED"
        return None

    if action.action == "SEARCH":
        if not action.query:
            raise ValueError(
                "SEARCH action requires a query."
            )

        if action.query in state.search_queries:
            raise ValueError(
                "Scout attempted to repeat a search query."
            )

        state.status = "SEARCHING"
        state.search_queries.append(action.query)

        results = search_tool(action.query)

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

        if not novel_results:
            state.search_results = []
            state.last_search_outcome = "NO_NOVEL_RESULTS"
            state.novelty_search_attempts += 1

            if (
                state.novelty_search_attempts
                >= state.max_novelty_search_attempts
            ):
                state.status = "FINISHED"

            return []

        state.search_results = novel_results
        state.last_search_outcome = "HAS_NOVEL_RESULTS"
        state.novelty_search_attempts = 0

        return novel_results

    if action.action == "READ":
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

        raw_content = read_tool(result.url)

        prepared = prepare_context(
            raw_content,
            max_tokens=SCOUT_READ_CONTEXT_MAX_TOKENS,
        )

        state.last_read_url = result.url
        state.last_read_content = prepared.content

        # A URL only becomes visited after a successful READ and
        # successful context preparation.
        state.visited_urls.append(result.url)

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

        if memory_service is not None:
            memory_service.mark_selected(result.url)

        return None

    if action.action == "FINISH":
        state.status = "FINISHED"
        return None

    raise ValueError(
        f"Unsupported Scout action: {action.action}"
    )


def run_scout(
    objective: str,
    search_tool: SearchTool,
    read_tool: ReadTool,
    max_steps: int = 5,
    max_novelty_search_attempts: int = 3,
    memory_service: InteractionMemoryService | None = None,
) -> ScoutState:
    state = ScoutState(
        objective=objective,
        max_steps=max_steps,
        max_novelty_search_attempts=max_novelty_search_attempts,
    )

    while state.status != "FINISHED":
        if state.steps >= state.max_steps:
            state.status = "FINISHED"
            break

        action = decide_next_action(state)

        try:
            execute_action(
                action=action,
                state=state,
                search_tool=search_tool,
                read_tool=read_tool,
                memory_service=memory_service,
            )
            state.last_error = None

        except ValueError as error:
            state.last_error = str(error)

        except WebToolError as error:
            state.last_error = f"Web tool failure: {error}"

        state.steps += 1

    return state
