from datetime import date

from openai import OpenAI

from klartext.domain.models import LetterResult
from klartext.domain.validation import verify
from klartext.services.extractor import extract
from klartext.domain.models import Deadline, LetterResult
from klartext.domain.dates import find_relative_days

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
    # Safety net: if the model quoted a period but left relative_days empty, read it from the quote.
    deadline = extraction.deadline
    if deadline is not None and deadline.iso_date is None and deadline.relative_days is None:
        deadline.relative_days = find_relative_days(deadline.source_span)
    unverified = verify(extraction, text)

    days_left, estimated = compute_days_left(extraction.deadline, today or date.today())
    if extraction.deadline is not None and extraction.deadline.iso_date is not None:
        days_left = (extraction.deadline.iso_date - (today or date.today())).days

    return LetterResult(
        id=doc_id,
        filename=filename,
        extraction=extraction,
        days_left=days_left,
        days_left_estimated=estimated,
        unverified_count=unverified,
        model_used=model,
        latency_ms=latency_ms,
    )

def compute_days_left(deadline: Deadline | None, today: date) -> tuple[int | None, bool]:
    """Days until the deadline, and whether that number is an estimate.

    Relative deadlines ("within 20 days") are counted from today, because the
    receipt date is unknown; the UI shows them as an estimate.
    """
    if deadline is None:
        return None, False
    if deadline.iso_date is not None:
        return (deadline.iso_date - today).days, False
    if deadline.relative_days is not None:
        return deadline.relative_days, True
    return None, False