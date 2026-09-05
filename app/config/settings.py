import os

from dotenv import load_dotenv


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not configured.")

MODEL_NAME = "gpt-5.6-terra"
MAX_OUTPUT_TOKENS = 500