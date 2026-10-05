from datetime import date

from openai import OpenAI

from klartext.domain.models import LetterResult
from klartext.domain.validation import verify
from klartext.services.extractor import extract

def analyze_letter(
    client: OpenAI,
    model: str,
    doc_id: str,
    filename: str,
    text: str,
    today: date | None = None,
) -> LetterResult:
    """Extract, verify and score one letter (single model; the cascade comes later)."""
    extraction, latency_ms = extract(client, model, text)
    unverified = verify(extraction, text)

    days_left = None
    if extraction.deadline is not None and extraction.deadline.iso_date is not None:
        days_left = (extraction.deadline.iso_date - (today or date.today())).days

    return LetterResult(
        id=doc_id,
        filename=filename,
        extraction=extraction,
        days_left=days_left,
        unverified_count=unverified,
        model_used=model,
        latency_ms=latency_ms,
    )