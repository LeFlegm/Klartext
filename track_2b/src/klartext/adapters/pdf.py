import io

import pdfplumber


class EmptyDocumentError(Exception):
    """Raised when a PDF contains no extractable text (e.g. a scanned image)."""

def extract_text(pdf_bytes: bytes) -> str:
    """Extract plain text from a digital PDF, page by page."""
    pages = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")

    text = "\n\n".join(pages).strip()
    if not text:
        raise EmptyDocumentError("No text found; the PDF may be a scanned image.")
    return text