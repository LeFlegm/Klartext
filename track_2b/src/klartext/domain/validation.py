import re
import unicodedata

from klartext.domain.dates import find_dates
from klartext.domain.models import Extraction, SourcedText

# Very short spans (e.g. "2026") would match almost any letter and prove nothing.
MIN_SPAN_LENGTH = 8

# Typographic variants that do not change meaning.
_EQUIVALENT_CHARS = str.maketrans({
    "\u2019": "'", "\u2018": "'",  # curly apostrophes
    "\u201c": '"', "\u201d": '"', "\u00ab": '"', "\u00bb": '"',  # quotes, guillemets
    "\u2013": "-", "\u2014": "-",  # en/em dashes
})


def normalize(text: str) -> str:
    """Make matching robust to line breaks, spacing, quote styles and case."""
    text = unicodedata.normalize("NFC", text).translate(_EQUIVALENT_CHARS)
    text = re.sub(r"\s+", " ", text)
    return text.strip().casefold()

def _is_supported(span: str, normalized_source: str) -> bool:
    span_n = normalize(span).strip(" .,;:")
    return len(span_n) > MIN_SPAN_LENGTH and span_n in normalized_source

def verify(extraction: Extraction, source: str) -> int:
    """Mark each point whose source span appears in the letter.

    Returns the number of unverified points (used to decide escalation to 70B).
    """

    normalized_source =normalize(source)
    points: list[SourcedText] = [extraction.sender, *extraction.actions, *extraction.consequences]
    if extraction.deadline is not None:
        points.append(extraction.deadline)

    for point in points:
        point.verified = _is_supported(point.source_span, normalized_source)

        # A deadline is only verified if its date really follows from its own quote.
        deadline = extraction.deadline
        if deadline is not None and deadline.iso_date is not None:
            deadline.verified = deadline.verified and deadline.iso_date in find_dates(deadline.source_span)
    return sum(not point.verified for point in points)