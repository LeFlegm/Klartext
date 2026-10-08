import io
import re
from collections import Counter

import pdfplumber



class EmptyDocumentError(Exception):
    """Raised when the pdf file is empty."""
    pass


def _key(line: str) -> str:
    # Digits become "#" so "Seite 1 von 2" and "Seite 2 von 2" match.
    return re.sub(r"\d+", "#", line.strip())


def strip_repeated_lines(pages: list[str]) -> list[str]:
    """Remove lines that repeat on two or more pages (footers, headers)."""
    if len(pages) < 2:
        return pages

    counts = Counter()
    for page in pages:
        keys = {_key(line) for line in page.splitlines() if line.strip()}
        counts.update(keys)

    repeated = {k for k, n in counts.items() if n >= 2}

    cleaned = []
    for page in pages:
        kept = [line for line in page.splitlines() if _key(line) not in repeated]
        cleaned.append("\n".join(kept))
    return cleaned

def extract_text(pdf_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    text = "\n".join(strip_repeated_lines(pages)).strip()
    if not text:
        raise EmptyDocumentError()
    return text