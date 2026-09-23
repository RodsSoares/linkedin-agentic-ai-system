import httpx
import pytest

from app.tools.brave_search import brave_search
from app.tools.errors import WebToolError


def test_brave_search_maps_provider_payload_to_search_results():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-subscription-token"] == "test-key"
        assert request.url.params["q"] == "agentic ai supply chain"
        assert request.url.params["count"] == "2"

        return httpx.Response(
            200,
            json={
                "web": {
                    "results": [
                        {
                            "title": "Agentic AI in Supply Chain",
                            "url": "https://example.com/one",
                            "description": "First result.",
                        },
                        {
                            "title": "AI Planning Systems",
                            "url": "https://example.com/two",
                            "description": "Second result.",
                        },
                    ]
                }
            },
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler)
    )

    try:
        results = brave_search(
            "agentic ai supply chain",
            api_key="test-key",
            max_results=2,
            client=client,
        )
    finally:
        client.close()

    assert len(results) == 2
    assert results[0].title == "Agentic AI in Supply Chain"
    assert results[0].url == "https://example.com/one"
    assert results[0].snippet == "First result."


def test_brave_search_requires_api_key():
    with pytest.raises(
        WebToolError,
        match="BRAVE_SEARCH_API_KEY is not configured",
    ):
        brave_search(
            "agentic ai",
            api_key="",
        )


def test_brave_search_rejects_empty_query():
    with pytest.raises(
        ValueError,
        match="non-empty query",
    ):
        brave_search(
            "   ",
            api_key="test-key",
        )


def test_brave_search_rejects_query_over_provider_character_limit():
    with pytest.raises(
        ValueError,
        match="600-character",
    ):
        brave_search(
            "x" * 601,
            api_key="test-key",
        )


def test_brave_search_wraps_http_status_errors():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429)

    client = httpx.Client(
        transport=httpx.MockTransport(handler)
    )

    try:
        with pytest.raises(
            WebToolError,
            match="HTTP 429",
        ):
            brave_search(
                "agentic ai",
                api_key="test-key",
                client=client,
            )
    finally:
        client.close()
