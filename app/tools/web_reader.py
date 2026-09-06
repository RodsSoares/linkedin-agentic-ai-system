from app.schemas.tools import SearchResult


FAKE_PAGE_CONTENT = {
    "https://example.com/posts/ai-agents-supply-chain": (
        "AI agents are being explored as a way to support supply chain "
        "planning and decision-making. These systems can coordinate "
        "specialized capabilities, analyze operational information, "
        "and assist humans in evaluating possible actions."
    ),
    "https://example.com/posts/genai-business-automation": (
        "Generative AI is increasingly being used to automate business "
        "processes. Agentic systems can combine reasoning with tools "
        "while keeping humans responsible for important decisions."
    ),
    "https://example.com/posts/quarterly-results": (
        "The company announced its quarterly financial results, "
        "highlighting revenue growth and improved profitability."
    ),
}


def web_reader(result: SearchResult) -> str:
    return FAKE_PAGE_CONTENT.get(
        result.url,
        "No content available for this page.",
    )