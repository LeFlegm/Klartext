from klartext.domain.models import Extraction
from klartext.eval.metrics import Run, evaluate_config, same_passage, score_letter, same_sender, SourcedText

LETTER = (
    "ADMINISTRATION CANTONALE DES IMPÔTS\n"
    "Office d'impôt du district de Morges\n"
    "Veuillez nous transmettre votre déclaration signée au plus tard le 31 octobre 2026.\n"
    "Sans réponse, votre taxation sera établie d'office.\n"
)


def make(consequences=("votre taxation sera établie d'office",), iso="2026-10-31") -> Extraction:
    return Extraction(
        document_type="tax",
        sender={"value": "Office d'impôt du district de Morges", "source_span": "Office d'impôt du district de Morges"},
        deadline={"value": "x", "source_span": "au plus tard le 31 octobre 2026", "iso_date": iso},
        actions=[{"value": "x", "source_span": "nous transmettre votre déclaration signée"}],
        consequences=[{"value": "x", "source_span": c} for c in consequences],
    )


TRUTH = make()


def test_same_passage_ignores_case_and_extra_words_but_not_other_sentences():
    assert same_passage("NOUS TRANSMETTRE votre déclaration", "Veuillez nous transmettre votre déclaration signée")
    assert not same_passage("votre taxation sera établie d'office", "nous transmettre votre déclaration signée")


def test_perfect_prediction_is_all_correct():
    pred = make()
    for p in (pred.sender, pred.deadline, pred.actions[0], pred.consequences[0]):
        p.verified = True
    s = score_letter(pred, TRUTH)
    assert s.document_type_ok and s.sender_ok and s.deadline_ok
    assert all(correct for correct, _ in s.points)
    assert (s.content_correct, s.content_predicted, s.truth_found, s.truth_total) == (2, 2, 2, 2)


def test_wrong_date_is_a_wrong_deadline_even_with_a_real_quote():
    s = score_letter(make(iso="2026-11-15"), TRUTH)
    assert not s.deadline_ok


def test_baseline_shows_invented_point_as_verified_while_the_check_flags_it():
    invented = make(consequences=("votre taxation sera établie d'office", "une amende de CHF 500"))
    runs = {"a": Run(invented, 1000)}
    runs70 = {"a": Run(invented, 5000)}
    args = (["a"], runs, runs70, {"a": LETTER}, {"a": TRUTH})

    baseline = evaluate_config("A", *args)["summary"]
    assert baseline["undetected errors"] == (1, 5)  # 1 wrong point among 5 points all shown as fine

    with_check = evaluate_config("C", *args)["summary"]
    assert with_check["undetected errors"] == (0, 4)
    assert with_check["caught errors"] == (1, 1)
    assert with_check["false alarms"] == (0, 4)


def test_cascade_escalates_only_when_8b_has_an_unverified_point():
    good, bad = make(), make(consequences=("une amende de CHF 500",))
    stems = ["clean", "dirty"]
    runs8 = {"clean": Run(good, 1000), "dirty": Run(bad, 1200)}
    runs70 = {"clean": Run(good, 5000), "dirty": Run(good, 6000)}
    texts = {s: LETTER for s in stems}
    truths = {s: TRUTH for s in stems}

    e = evaluate_config("E", stems, runs8, runs70, texts, truths)
    assert e["escalated"] == 1
    assert e["latencies"] == [1000, 1200 + 6000]
    assert e["summary"]["wrong points"] == (0, 8)  # the escalated letter now uses the correct 70B answer


def test_failed_run_is_counted_not_scored():
    runs = {"a": Run(None, 900)}
    r = evaluate_config("C", ["a"], runs, runs, {"a": LETTER}, {"a": TRUTH})
    assert r["failed"] == 1 and r["summary"]["sender correct"] == (0, 0)

def test_sender_matches_on_quote_not_on_english_value():
    pred = SourcedText(value="SantePlus health insurance", source_span="Assurance Maladie SantePlus")
    truth = SourcedText(value="Assurance Maladie SantePlus", source_span="Assurance Maladie SantePlus")
    assert same_sender(pred, truth)


def test_longer_letterhead_quote_still_counts_as_same_sender():
    pred = SourcedText(value="x", source_span="Assurance Maladie SantePlus Département des primes")
    truth = SourcedText(value="y", source_span="Assurance Maladie SantePlus")
    assert same_sender(pred, truth)