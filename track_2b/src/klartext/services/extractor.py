import re
import time

from openai import OpenAI
from pydantic import ValidationError

from klartext.domain.models import Extraction

SYSTEM_PROMPT = """You extract key facts from official Swiss letters.

Rules:
- Use ONLY information written in the letter. Never add legal knowledge of your own.
- "source_span": copy the exact words from the letter, character for character, in the letter's
  original language. Do not drop, add or reorder any word.
- "value": a short summary IN ENGLISH, even when the letter is in French, German or Italian.
- sender: the authority or organisation that wrote the letter (usually in the letterhead or signature),
  never the person or household the letter is addressed to.
- The reader is the recipient of the letter; actions and deadlines are what the recipient must do.
- document_type is one of: "tax", "health_insurance", "debt_enforcement", "other".
- deadline: the date by which the reader must act, with iso_date as YYYY-MM-DD; null if there is none.
- consequences: only what the letter itself says happens if the reader does nothing; empty list if nothing is stated.

Example (letter in German, values in English):
Letter excerpt: "Krankenkasse Musterhof ... Bitte bezahlen Sie den offenen Betrag von CHF 412.50
bis spätestens 15. November 2026. Andernfalls leiten wir die Betreibung ein."
Output:
{"document_type": "health_insurance",
 "sender": {"value": "Musterhof health insurance", "source_span": "Krankenkasse Musterhof"},
 "deadline": {"value": "Pay by 15 November 2026", "source_span": "bis spätestens 15. November 2026", "iso_date": "2026-11-15"},
 "actions": [{"value": "Pay the outstanding CHF 412.50", "source_span": "bezahlen Sie den offenen Betrag von CHF 412.50"}],
 "consequences": [{"value": "Debt enforcement will be started", "source_span": "Andernfalls leiten wir die Betreibung ein"}]}

Return ONLY a JSON object for the letter you are given, no markdown, in the same shape."""


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