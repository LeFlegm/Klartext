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


def _edge_indexes(lines: list[str]) -> set[int]:
    """Indexes of the first and last non-empty line of a page."""
    filled = [i for i, line in enumerate(lines) if line.strip()]
    return {filled[0], filled[-1]} if filled else set()


def strip_repeated_lines(pages: list[str]) -> list[str]:
    """Remove page headers/footers: edge lines that repeat on 2+ pages."""
    if len(pages) < 2:
        return pages

    split = [page.splitlines() for page in pages]

    counts = Counter()
    for lines in split:
        counts.update({_key(lines[i]) for i in _edge_indexes(lines)})
    repeated = {k for k, n in counts.items() if n >= 2}

    cleaned = []
    for lines in split:
        edges = _edge_indexes(lines)
        kept = [
            line for i, line in enumerate(lines)
            if not (i in edges and _key(line) in repeated)
        ]
        cleaned.append("\n".join(kept))
    return cleaned

def extract_text(pdf_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    text = "\n".join(strip_repeated_lines(pages)).strip()
    if not text:
        raise EmptyDocumentError()
    return text