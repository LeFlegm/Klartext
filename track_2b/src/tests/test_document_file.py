import pytest
from fastapi import HTTPException

from klartext.api.main import StoredDocument, documents, get_original_pdf


def test_original_pdf_is_served_from_memory():
    documents["t"] = StoredDocument(filename="a.pdf", text="x", pdf=b"%PDF-1.4 test")
    try:
        response = get_original_pdf("t")
        assert response.media_type == "application/pdf"
        assert response.body == b"%PDF-1.4 test"
    finally:
        documents.pop("t", None)


def test_unknown_document_file_is_404():
    with pytest.raises(HTTPException) as error:
        get_original_pdf("nope")
    assert error.value.status_code == 404
