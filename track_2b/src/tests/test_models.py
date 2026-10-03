from datetime import date

import pytest
from pydantic import ValidationError

from klartext.domain.models import Extraction


def test_valid_extraction_parses_deadline():
    e = Extraction(
        document_type="tax",
        sender={"value": "Office d'impôt de Morges", "source_span": "Office d'impôt du district de Morges"},
        deadline={
            "value": "31 octobre 2026",
            "source_span": "au plus tard le 31 octobre 2026",
            "iso_date": "2026-10-31",
        },
    )
    assert e.deadline.iso_date == date(2026, 10, 31)  # string converted to a real date
    assert e.sender.verified is False  # only our validator may set this
    assert e.actions == []  # optional lists default to empty


def test_unknown_document_type_is_rejected():
    with pytest.raises(ValidationError):
        Extraction(document_type="Steuer", sender={"value": "x", "source_span": "x"})