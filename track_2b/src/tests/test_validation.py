from klartext.domain.models import Extraction
from klartext.domain.validation import verify

from klartext.domain.validation import normalize

LETTER = (
    "ADMINISTRATION CANTONALE DES IMPÔTS\n"
    "Office d'impôt du district de Morges\n"
    "Nous vous prions de bien vouloir nous transmettre votre déclaration dûment complétée et\n"
    "signée, accompagnée des pièces justificatives, au plus tard le 31 octobre 2026.\n"
)

def make(span: str) -> Extraction:
    return Extraction(document_type="tax", sender={"value": "x", "source_span": span})

def test_span_across_line_break_is_verified():
    e = make("votre déclaration dûment complétée et signée")
    assert verify(e, LETTER) == 0
    assert e.sender.verified


def test_case_is_ignored():
    e = make("Administration cantonale des impôts")
    assert verify(e, LETTER) == 0


def test_curly_apostrophe_matches_straight_one():
    e = make("Office d\u2019impôt du district")  # model used a curly apostrophe
    assert verify(e, LETTER) == 0


def test_invented_span_is_not_verified():
    e = make("une amende de CHF 500")
    assert verify(e, LETTER) == 1
    assert not e.sender.verified


def test_too_short_span_is_not_verified():
    e = make("2026")
    assert verify(e, LETTER) == 1

def test_hyphenated_line_break_is_joined():
    source = "Sollten Sie diese Zahlungs-\nfrist verpassen"
    assert normalize("diese Zahlungsfrist verpassen") in normalize(source)