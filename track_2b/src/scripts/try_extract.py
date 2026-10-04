"""Manual check: run the extractor on one letter with both models and verify the output."""
import sys
from pathlib import Path

from dotenv import load_dotenv

from klartext.adapters.llm import get_client
from klartext.adapters.pdf import extract_text
from klartext.domain.validation import verify
from klartext.services.extractor import extract

load_dotenv("../.env")

pdf_path = Path(sys.argv[1] if len(sys.argv) > 1 else "../data/CH_VD_TAX_001_fr.pdf")
letter = extract_text(pdf_path.read_bytes())
client = get_client()

for model in ("apertus-v1.5-8b", "apertus-v1.5-70b"):
    extraction, latency_ms = extract(client, model, letter)
    unverified = verify(extraction, letter)
    print(f"=== {model}: {latency_ms} ms, {unverified} unverified")
    print(extraction.model_dump_json(indent=2))