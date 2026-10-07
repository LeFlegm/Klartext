"""Scoring of extractions against hand-written ground truth. Pure functions, no LLM calls."""
import re
from dataclasses import dataclass, field

from klartext.domain.models import Deadline, Extraction, SourcedText
from klartext.domain.validation import fill_relative_days, normalize, verify

# Two passages count as the same when at least half of their words overlap (F1).
MATCH_THRESHOLD = 0.5


def token_f1(a: str, b: str) -> float:
    """Word overlap between two texts, ignoring case, accents style and spacing."""
    words_a = set(re.findall(r"\w+", normalize(a)))
    words_b = set(re.findall(r"\w+", normalize(b)))
    common = words_a & words_b
    if not common:
        return 0.0
    precision, recall = len(common) / len(words_a), len(common) / len(words_b)
    return 2 * precision * recall / (precision + recall)


def same_passage(a: str, b: str) -> bool:
    return token_f1(a, b) >= MATCH_THRESHOLD


def _deadline_key(e: Extraction) -> tuple | None:
    """What a deadline says, ignoring wording; None when the letter gives no usable deadline."""
    d = e.deadline
    if d is None or (d.iso_date is None and d.relative_days is None):
        return None
    return (d.iso_date, d.relative_days)


def points_of(e: Extraction) -> list[tuple[str, SourcedText]]:
    """Every point shown to the user, with its kind. Keep in sync with validation.verify."""
    points: list[tuple[str, SourcedText]] = [("sender", e.sender)]
    if _deadline_key(e) is not None:
        points.append(("deadline", e.deadline))
    points += [("action", p) for p in e.actions]
    points += [("consequence", p) for p in e.consequences]
    return points


def _is_correct(kind: str, point: SourcedText, truth: Extraction) -> bool:
    if kind == "sender":
        return same_passage(point.value, truth.sender.value)
    if kind == "deadline":
        assert isinstance(point, Deadline)
        return (point.iso_date, point.relative_days) == _deadline_key(truth)
    pool = truth.actions if kind == "action" else truth.consequences
    # Quotes are verbatim and in the letter's language, so matching on them avoids judging English paraphrases.
    return any(same_passage(point.source_span, t.source_span) for t in pool)


def judged_points(pred: Extraction, truth: Extraction) -> list[tuple[str, SourcedText, bool]]:
    """Each predicted point with its kind and whether it matches the ground truth."""
    return [(kind, point, _is_correct(kind, point, truth)) for kind, point in points_of(pred)]

@dataclass
class LetterScore:
    document_type_ok: bool
    sender_ok: bool
    deadline_ok: bool
    points: list[tuple[bool, bool]] = field(default_factory=list)  # (correct, shown as verified)
    content_predicted: int = 0  # predicted actions + consequences
    content_correct: int = 0  # ... that match the ground truth
    truth_total: int = 0  # true actions + consequences
    truth_found: int = 0  # ... that some prediction of the same kind matches


def score_letter(pred: Extraction, truth: Extraction) -> LetterScore:
    """Compare one extraction (verified flags already set) with its ground truth."""
    score = LetterScore(
        document_type_ok=pred.document_type == truth.document_type,
        sender_ok=same_passage(pred.sender.value, truth.sender.value),
        deadline_ok=_deadline_key(pred) == _deadline_key(truth),
    )
    for kind, point in points_of(pred):
        correct = _is_correct(kind, point, truth)
        score.points.append((correct, point.verified))
        if kind in ("action", "consequence"):
            score.content_predicted += 1
            score.content_correct += correct
    for truths, preds in ((truth.actions, pred.actions), (truth.consequences, pred.consequences)):
        for t in truths:
            score.truth_total += 1
            score.truth_found += any(same_passage(p.source_span, t.source_span) for p in preds)
    return score


def summarize(scores: list[LetterScore]) -> dict[str, tuple[int, int]]:
    """Each metric as (numerator, denominator); the caller decides how to print it."""
    points = [p for s in scores for p in s.points]
    wrong = [p for p in points if not p[0]]
    right = [p for p in points if p[0]]
    shown_verified = [p for p in points if p[1]]
    return {
        "document type correct": (sum(s.document_type_ok for s in scores), len(scores)),
        "sender correct": (sum(s.sender_ok for s in scores), len(scores)),
        "deadline correct": (sum(s.deadline_ok for s in scores), len(scores)),
        "content precision": (sum(s.content_correct for s in scores), sum(s.content_predicted for s in scores)),
        "content recall": (sum(s.truth_found for s in scores), sum(s.truth_total for s in scores)),
        "wrong points": (len(wrong), len(points)),
        # Of the points shown to the user as fine, how many are wrong (the key metric).
        "undetected errors": (sum(1 for _, v in wrong if v), len(shown_verified)),
        "caught errors": (sum(1 for _, v in wrong if not v), len(wrong)),
        "false alarms": (sum(1 for _, v in right if not v), len(right)),
    }


@dataclass
class Run:
    """One model's raw answer for one letter."""

    extraction: Extraction | None  # None: the model never produced valid JSON
    latency_ms: int = 0


def checked(extraction: Extraction, text: str, check: bool) -> tuple[Extraction, int]:
    """Post-process a raw extraction the way the pipeline does; returns it and its unverified count."""
    ex = extraction.model_copy(deep=True)
    fill_relative_days(ex)  # deterministic reading of "within 20 days"; applied in every configuration
    if check:
        return ex, verify(ex, text)
    for _, point in points_of(ex):
        point.verified = True  # without the check, every point is shown as fine
    return ex, 0


def outcome_for(config: str, r8: Run, r70: Run, text: str) -> tuple[Extraction | None, int, bool]:
    """What the user gets under a configuration: (extraction, latency in ms, escalated to 70B)."""
    if config in ("A", "B", "C", "D"):  # A/B: 8B/70B raw, C/D: 8B/70B + check
        run = r8 if config in ("A", "C") else r70
        if run.extraction is None:
            return None, run.latency_ms, False
        ex, _ = checked(run.extraction, text, check=config in ("C", "D"))
        return ex, run.latency_ms, False
    # E, cascade: keep the 8B answer if every point is verified, otherwise use the 70B answer.
    if r8.extraction is not None:
        ex8, unverified = checked(r8.extraction, text, check=True)
        if unverified == 0:
            return ex8, r8.latency_ms, False
    total = r8.latency_ms + r70.latency_ms
    if r70.extraction is None:
        return None, total, True
    ex70, _ = checked(r70.extraction, text, check=True)
    return ex70, total, True


def evaluate_config(config, stems, runs8, runs70, texts, truths) -> dict:
    scores, latencies, escalated, failed = [], [], 0, 0
    for stem in stems:
        ex, latency, esc = outcome_for(config, runs8[stem], runs70[stem], texts[stem])
        latencies.append(latency)
        escalated += esc
        if ex is None:
            failed += 1
        else:
            scores.append(score_letter(ex, truths[stem]))
    return {"summary": summarize(scores), "latencies": latencies, "escalated": escalated,
            "failed": failed, "n": len(stems)}