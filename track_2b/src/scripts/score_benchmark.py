"""Score a saved benchmark run: five configurations side by side, plus the points worth reading."""
import json
import sys
from pathlib import Path

from klartext.adapters.pdf import extract_text
from klartext.domain.models import Extraction
from klartext.domain.validation import verify
from klartext.eval.metrics import Run, evaluate_config, judged_points, outcome_for, points_of, same_passage

DATA = Path("../data")
CONFIGS = {"A": "A 8B raw", "B": "B 70B raw", "C": "C 8B+check", "D": "D 70B+check", "E": "E cascade"}


def load_run(path: Path) -> Run:
    record = json.loads(path.read_text(encoding="utf-8"))
    if "error" in record:
        return Run(None, 0)
    return Run(Extraction.model_validate(record["extraction"]), record["latency_ms"])


def load_truth(stem: str, text: str) -> Extraction:
    truth = Extraction.model_validate_json((DATA / "ground_truth" / f"{stem}.json").read_text(encoding="utf-8"))
    # Sanity check: every quote in the ground truth must really be in the letter.
    probe = truth.model_copy(deep=True)
    if verify(probe, text):
        print(f"WARNING {stem}: ground-truth quote(s) not found in the letter:")
        for kind, point in points_of(probe):
            if not point.verified:
                print(f"   {kind}: {point.source_span[:80]}")
    return truth


def frac(pair: tuple[int, int]) -> str:
    num, den = pair
    return f"{num}/{den}" if den else "-"


def print_table(results: dict) -> None:
    print(f"\n{'':<26}" + "".join(f"{name:>13}" for name in CONFIGS.values()))
    rows = [("letters scored", lambda r: f"{r['n'] - r['failed']}/{r['n']}")]
    rows += [(key, lambda r, k=key: frac(r["summary"][k])) for key in next(iter(results.values()))["summary"]]
    rows += [
        ("mean latency (ms)", lambda r: f"{sum(r['latencies']) / max(len(r['latencies']), 1):.0f}"),
        ("escalated to 70B", lambda r: f"{r['escalated']}/{r['n']}" if r["escalated"] or r is results["E"] else "-"),
    ]
    for label, cell in rows:
        print(f"{label:<26}" + "".join(f"{cell(results[c]):>13}" for c in CONFIGS))


def print_review(stems, runs8, runs70, texts, truths) -> None:
    """Every wrong or flagged point and every missed true point: read these before trusting the numbers."""
    print("\nPoints to review (configurations C and D)")
    lines = []
    for config, short in (("C", "8b"), ("D", "70b")):
        for stem in stems:
            ex, _, _ = outcome_for(config, runs8[stem], runs70[stem], texts[stem])
            if ex is None:
                lines.append(f"{stem:<26} {short:<4} NO VALID JSON")
                continue
            for kind, point, correct in judged_points(ex, truths[stem]):
                if not correct or not point.verified:
                    tag = f"{'WRONG' if not correct else 'ok':<6}{'verified' if point.verified else 'FLAGGED'}"
                    lines.append(f"{stem:<26} {short:<4} {kind:<11} {tag:<15} {point.source_span[:50]}")
            for kind, truths_of, preds in (("action", truths[stem].actions, ex.actions),
                                           ("consequence", truths[stem].consequences, ex.consequences)):
                for t in truths_of:
                    if not any(same_passage(p.source_span, t.source_span) for p in preds):
                        lines.append(f"{stem:<26} {short:<4} {kind:<11} {'MISSED':<15} {t.source_span[:50]}")
    print("\n".join(lines) if lines else "  nothing: every point is correct and verified")


if __name__ == "__main__":
    runs_root = DATA / "runs"
    run_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else max(runs_root.iterdir())
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    print(f"run {run_dir.name}  prompt {meta['prompt_sha1']}  temperature {meta['temperature']}  models {list(meta['models'].values())}")

    stems = sorted(p.stem for p in (run_dir / "8b").glob("*.json"))
    texts = {s: extract_text((DATA / f"{s}.pdf").read_bytes()) for s in stems}
    truths = {s: load_truth(s, texts[s]) for s in stems}
    runs8 = {s: load_run(run_dir / "8b" / f"{s}.json") for s in stems}
    runs70 = {s: load_run(run_dir / "70b" / f"{s}.json") for s in stems}

    results = {c: evaluate_config(c, stems, runs8, runs70, texts, truths) for c in CONFIGS}
    print_table(results)
    print_review(stems, runs8, runs70, texts, truths)