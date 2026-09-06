from openai import OpenAI

from app.config.settings import MODEL_NAME, OPENAI_API_KEY
from app.schemas.post import PostCandidate
from app.schemas.scout import ScoutAction, ScoutState
from app.schemas.tools import SearchResult
from app.tools.web_reader import web_reader
from app.tools.web_search import web_search


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


def execute_action(
    action: ScoutAction,
    state: ScoutState,
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

        results = web_search(action.query)
        state.search_results = results

        return results

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
        state.visited_urls.append(action.url)

        content = web_reader(result)

        state.last_read_url = result.url
        state.last_read_content = content

        return content

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

        candidate = PostCandidate(
            post_id=result.url,
            author_name="Unknown",
            post_text=state.last_read_content,
            post_url=result.url,
        )

        state.candidates.append(candidate)

        return None

    if action.action == "FINISH":
        state.status = "FINISHED"
        return None

    raise ValueError(
        f"Unsupported Scout action: {action.action}"
    )


def run_scout(
    objective: str,
    max_steps: int = 5,
) -> ScoutState:
    state = ScoutState(
        objective=objective,
        max_steps=max_steps,
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
            )
            state.last_error = None

        except ValueError as error:
            state.last_error = str(error)

        state.steps += 1

    return state