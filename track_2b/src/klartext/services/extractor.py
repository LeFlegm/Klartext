import re
import time

from openai import OpenAI
from pydantic import ValidationError

from klartext.domain.models import Extraction

SYSTEM_PROMPT = """You extract key facts from official Swiss letters.

Rules:
- Use ONLY information written in the letter. Never add legal knowledge of your own.
- Every "source_span" must be copied word for word from the letter, in the letter's original language.
- Write every "value" as a short plain-English phrase.
- document_type is one of: "tax", "health_insurance", "debt_enforcement", "other".
- deadline: the date by which the reader must act, with iso_date as YYYY-MM-DD; null if there is none.
- consequences: only what the letter itself says happens if the reader does nothing; empty list if nothing is stated.

Return ONLY a JSON object, no markdown, in this shape:
{"document_type": "...",
 "sender": {"value": "...", "source_span": "..."},
 "deadline": {"value": "...", "source_span": "...", "iso_date": "YYYY-MM-DD"} or null,
 "actions": [{"value": "...", "source_span": "..."}],
 "consequences": [{"value": "...", "source_span": "..."}]}"""


def _parse(raw: str) -> Extraction:
    # Models sometimes wrap JSON in ```json fences or add text around it; keep the outermost object.
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match is None:
        raise ValueError("No JSON object found in model output")
    return Extraction.model_validate_json(match.group(0))


def extract(client: OpenAI, model: str, letter: str) -> tuple[Extraction, int]:
    """Ask the model for an Extraction, retrying once with the error message.

    Returns the extraction and the total latency in milliseconds.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"LETTER:\n{letter}"},
    ]
    start = time.perf_counter()
    for attempt in range(2):
        resp = client.chat.completions.create(model=model, messages=messages, temperature=0)
        raw = resp.choices[0].message.content or ""
        try:
            return _parse(raw), int((time.perf_counter() - start) * 1000)
        except (ValueError, ValidationError) as e:
            if attempt == 1:
                raise
            # Show the model its own output and the error, then ask for a fix.
            messages += [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": f"Your output was invalid: {e}. Return only the corrected JSON."},
            ]