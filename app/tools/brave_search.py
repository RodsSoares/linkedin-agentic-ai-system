import httpx

from app.config.settings import (
    BRAVE_SEARCH_API_KEY,
    WEB_SEARCH_MAX_RESULTS,
    WEB_SEARCH_TIMEOUT_SECONDS,
)
from app.schemas.tools import SearchResult
from app.tools.errors import WebToolError


BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
BRAVE_QUERY_MAX_CHARACTERS = 600
BRAVE_QUERY_MAX_WORDS = 75


def brave_search(
    query: str,
    *,
    api_key: str | None = None,
    max_results: int = WEB_SEARCH_MAX_RESULTS,
    timeout_seconds: float = WEB_SEARCH_TIMEOUT_SECONDS,
    client: httpx.Client | None = None,
) -> list[SearchResult]:
    normalized_query = query.strip()

    if not normalized_query:
        raise ValueError("Brave search requires a non-empty query.")

    if len(normalized_query) > BRAVE_QUERY_MAX_CHARACTERS:
        raise ValueError(
            "Brave search query exceeds the 600-character provider limit."
        )

    if len(normalized_query.split()) > BRAVE_QUERY_MAX_WORDS:
        raise ValueError(
            "Brave search query exceeds the 75-word provider limit."
        )

    if not 1 <= max_results <= 20:
        raise ValueError("max_results must be between 1 and 20.")

    resolved_api_key = (
        BRAVE_SEARCH_API_KEY
        if api_key is None
        else api_key
    )

    if not resolved_api_key or not resolved_api_key.strip():
        raise WebToolError(
            "BRAVE_SEARCH_API_KEY is not configured."
        )

    owns_client = client is None
    http_client = client or httpx.Client(
        timeout=timeout_seconds,
        follow_redirects=False,
    )

    try:
        response = http_client.get(
            BRAVE_SEARCH_URL,
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": resolved_api_key,
            },
            params={
                "q": normalized_query,
                "count": max_results,
            },
        )
        response.raise_for_status()
        payload = response.json()

    except httpx.TimeoutException as error:
        raise WebToolError(
            "Brave Search request timed out."
        ) from error

    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        raise WebToolError(
            f"Brave Search returned HTTP {status_code}."
        ) from error

    except httpx.HTTPError as error:
        raise WebToolError(
            "Brave Search request failed."
        ) from error

    except ValueError as error:
        raise WebToolError(
            "Brave Search returned an invalid JSON response."
        ) from error

    finally:
        if owns_client:
            http_client.close()

    raw_results = payload.get("web", {}).get("results", [])

    if not isinstance(raw_results, list):
        raise WebToolError(
            "Brave Search response has an invalid web.results payload."
        )

    results: list[SearchResult] = []

    for item in raw_results[:max_results]:
        if not isinstance(item, dict):
            continue

        title = item.get("title")
        url = item.get("url")
        description = item.get("description", "")

        if not isinstance(title, str) or not title.strip():
            continue

        if not isinstance(url, str) or not url.strip():
            continue

        if not isinstance(description, str):
            description = ""

        results.append(
            SearchResult(
                title=title.strip(),
                url=url.strip(),
                snippet=description.strip(),
            )
        )

    return results
