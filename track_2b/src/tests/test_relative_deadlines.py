from datetime import date

from klartext.domain.models import Deadline, Extraction
from klartext.domain.validation import verify
from klartext.services.pipeline import compute_days_left
from klartext.domain.dates import find_relative_days

LETTER = "Veuillez verser la somme due dans un délai de 20 jours."


def make(span: str, relative_days: int) -> Extraction:
    return Extraction(
        document_type="debt_enforcement",
        sender={"value": "x", "source_span": "Veuillez verser la somme"},
        deadline={"value": "x", "source_span": span, "relative_days": relative_days},
    )


def test_relative_deadline_with_matching_number_is_verified():
    e = make("dans un délai de 20 jours", 20)
    verify(e, LETTER)
    assert e.deadline.verified


def test_relative_deadline_with_wrong_number_is_flagged():
    e = make("dans un délai de 20 jours", 2)  # "2" must not match inside "20"
    verify(e, LETTER)
    assert not e.deadline.verified


def test_relative_deadline_is_counted_from_today_as_estimate():
    deadline = Deadline(value="x", source_span="x", relative_days=20)
    assert compute_days_left(deadline, date(2026, 10, 6)) == (20, True)


def test_absolute_deadline_is_exact():
    deadline = Deadline(value="x", source_span="x", iso_date=date(2026, 10, 31))
    assert compute_days_left(deadline, date(2026, 10, 6)) == (25, False)

def test_finds_relative_days_in_swiss_languages():
    assert find_relative_days("dans un délai de 20 jours") == 20
    assert find_relative_days("innert 30 Tagen") == 30
    assert find_relative_days("entro 30 giorni") == 30
    assert find_relative_days("au plus tard le 31 octobre 2026") is None