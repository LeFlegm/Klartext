"""Run both Apertus models on every letter that has ground truth and save the raw answers."""
import hashlib
import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from pydantic import ValidationError

from klartext.adapters.llm import get_client
from klartext.adapters.pdf import extract_text
from klartext.services.extractor import SYSTEM_PROMPT, extract

MODELS = {"8b": "apertus-v1.5-8b", "70b": "apertus-v1.5-70b"}
DATA = Path("../data")

def letters_with_ground_truth() -> list[str]:
    stems = sorted(p.stem for p in (DATA / "ground_truth").glob("*.json"))
    missing = [s for s in stems if not (DATA / f"{s}.pdf").exists()]
    for stem in missing:
        print(f"WARNING: ground truth {stem}.json has no matching PDF in data/, skipped")
    return [s for s in stems if s not in missing]

def run(client, stems: list[str], out_dir: Path) -> None:
    """Save each model's raw (unchecked) extraction, so scoring can be repeated without API calls."""
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "started": datetime.now().isoformat(timespec="seconds"),
        "models": MODELS,
        "temperature": 0,
        "prompt_sha1": hashlib.sha1(SYSTEM_PROMPT.encode("utf-8")).hexdigest()[:12],
        "letters": stems,
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    for stem in stems:
        text = extract_text((DATA / f"{stem}.pdf").read_bytes())
        for short, model in MODELS.items():
            record = {"letter": stem, "model": model}
            try:
                extraction, latency_ms = extract(client, model, text)
                record |= {"latency_ms": latency_ms, "extraction": extraction.model_dump(mode="json")}
            except (ValueError, ValidationError) as e:  # the model never produced valid JSON
                record["error"] = str(e)
            folder = out_dir / short
            folder.mkdir(exist_ok=True)
            (folder / f"{stem}.json").write_text(
                json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            status = "ERROR" if "error" in record else f"{record['latency_ms']} ms"
            print(f"{stem:<28} {short:<4} {status}")


if __name__ == "__main__":
    load_dotenv("../.env")
    stems = letters_with_ground_truth()
    out_dir = DATA / "runs" / datetime.now().strftime("%Y%m%d-%H%M%S")
    print(f"{len(stems)} letters -> {out_dir}")
    run(get_client(), stems, out_dir)
    print(f"done: python -m scripts.score_benchmark {out_dir}")