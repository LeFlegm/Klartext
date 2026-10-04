import os

from openai import OpenAI


def get_client() -> OpenAI:
    """OpenAI-compatible client.

    The endpoint comes only from LLM_BASE_URL: the hackathon API during development,
    a locally served Apertus (e.g. vLLM) in an air-gapped deployment.
    """
    return OpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])