import os

from dotenv import load_dotenv


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not configured.")

BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")

MODEL_NAME = "gpt-5.6-terra"
MAX_OUTPUT_TOKENS = 500

WEB_SEARCH_TIMEOUT_SECONDS = 10.0
WEB_READ_TIMEOUT_SECONDS = 10.0
WEB_SEARCH_MAX_RESULTS = 5
WEB_READ_MAX_BYTES = 1_000_000

WEB_TOOL_MODE = os.getenv("WEB_TOOL_MODE", "fake").strip().lower()

if WEB_TOOL_MODE not in {"fake", "real"}:
    raise RuntimeError(
        "WEB_TOOL_MODE must be either 'fake' or 'real'."
    )

CONTEXT_TOKEN_ENCODING = os.getenv(
    "CONTEXT_TOKEN_ENCODING",
    "o200k_base",
)

SCOUT_READ_CONTEXT_MAX_TOKENS = int(
    os.getenv("SCOUT_READ_CONTEXT_MAX_TOKENS", "1800")
)

RESEARCH_READ_CONTEXT_MAX_TOKENS = int(
    os.getenv("RESEARCH_READ_CONTEXT_MAX_TOKENS", "2500")
)

RESEARCH_TOTAL_READ_CONTEXT_MAX_TOKENS = int(
    os.getenv("RESEARCH_TOTAL_READ_CONTEXT_MAX_TOKENS", "8000")
)
