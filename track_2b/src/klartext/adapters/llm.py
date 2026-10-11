import os

from openai import OpenAI

class LLMConfigError(RuntimeError):
    """Raised when the LLM endpoint is not configured."""


def get_client() -> OpenAI:
    base_url = os.environ.get("LLM_BASE_URL")
    api_key = os.environ.get("LLM_API_KEY")
    if not base_url or not api_key:
        raise LLMConfigError("LLM_BASE_URL and LLM_API_KEY are not set. Copy .env.example to .env and fill them in.")
    return OpenAI(base_url=base_url, api_key=api_key)