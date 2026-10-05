from datetime import date

from klartext.domain.dates import find_dates
from klartext.domain.models import Extraction
from klartext.domain.validation import verify


def test_finds_dates_in_swiss_languages_and_formats():
    assert find_dates("au plus tard le 31 octobre 2026") == {date(2026, 10, 31)}
    assert find_dates("avant le 1er novembre 2026") == {date(2026, 11, 1)}
    assert find_dates("bis spätestens 15. November 2026") == {date(2026, 11, 15)}
    assert find_dates("entro il 31 ottobre 2026") == {date(2026, 10, 31)}
    assert find_dates("Frist: 31.10.2026") == {date(2026, 10, 31)}


def test_ignores_impossible_dates_and_unknown_words():
    assert find_dates("31.02.2026") == set()
    assert find_dates("innert 12 Monate 2026") == set()


LETTER = "Veuillez répondre au plus tard le 31 octobre 2026. Merci de respecter cette date."


def make(span: str, iso: str) -> Extraction:
    return Extraction(
        document_type="tax",
        sender={"value": "x", "source_span": "Veuillez répondre"},
        deadline={"value": "x", "source_span": span, "iso_date": iso},
    )

def test_deadline_matching_its_quote_is_verified():
    e = make("au plus tard le 31 octobre 2026", "2026-10-31")
    verify(e, LETTER)
    assert e.deadline.verified


def test_invented_date_behind_real_quote_is_flagged():
    e = make("au plus tard le 31 octobre 2026", "2026-11-15")  # quote is real, date is not
    verify(e, LETTER)
    assert not e.deadline.verified


def test_quote_without_any_date_is_flagged():
    e = make("respecter cette date", "2026-10-31")  # quote exists but contains no date
    verify(e, LETTER)
    assert not e.deadline.verified