"""Quick manual check: send the same question to both Apertus models and time them."""
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv("../.env")
client = OpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])


def ask(model: str, question: str) -> None:
    start = time.perf_counter()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": question}],
        temperature=0,
    )
    elapsed = time.perf_counter() - start
    print(f"--- {model} ({elapsed:.1f}s)")
    print(resp.choices[0].message.content)
    print()


if __name__ == "__main__":
    q = "In two sentences: what is a Zahlungsbefehl in Switzerland, and what can the recipient do?"
    ask("apertus-v1.5-8b", q)
    ask("apertus-v1.5-70b", q)