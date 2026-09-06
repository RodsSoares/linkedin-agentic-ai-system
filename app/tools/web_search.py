from app.schemas.tools import SearchResult


FAKE_SEARCH_RESULTS = [
    SearchResult(
        title="AI agents are changing supply chain planning",
        url="https://example.com/posts/ai-agents-supply-chain",
        snippet=(
            "A discussion about using AI agents to support "
            "planning and decision-making in supply chains."
        ),
    ),
    SearchResult(
        title="Generative AI and the future of business automation",
        url="https://example.com/posts/genai-business-automation",
        snippet=(
            "How Generative AI is being applied to automate "
            "business processes and support human decisions."
        ),
    ),
    SearchResult(
        title="Quarterly financial results announced",
        url="https://example.com/posts/quarterly-results",
        snippet=(
            "A company announces its latest quarterly "
            "financial results and celebrates revenue growth."
        ),
    ),
]


def web_search(query: str) -> list[SearchResult]:
    return FAKE_SEARCH_RESULTS