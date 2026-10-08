from datetime import date

from openai import OpenAI
from pydantic import ValidationError

from klartext.domain.models import LetterResult
from klartext.domain.validation import verify
from klartext.services.extractor import extract
from klartext.domain.models import Deadline, LetterResult
from klartext.domain.validation import fill_relative_days,verify


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
    fill_relative_days(extraction)
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

def analyze_with_cascade(client, small, large, doc_id, filename, text, today=None, analyze=analyze_letter):
    """Try the small model first; escalate to the large one if anything is unverified or the output is invalid."""
    small_result = None
    try:
        small_result = analyze(client, small, doc_id, filename, text, today)
        if small_result.unverified_count == 0:
            return small_result
    except (ValueError, ValidationError):
        pass  # fall through to the large model

    try:
        large_result = analyze(client, large, doc_id, filename, text, today)
    except (ValueError, ValidationError):
        if small_result is not None:
            return small_result  # keep the flagged small-model answer rather than failing
        raise

    large_result.escalated = True
    if small_result is not None:
        large_result.latency_ms += small_result.latency_ms
    return large_result

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