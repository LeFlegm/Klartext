"""Run the full pipeline on every PDF in data/ and print the triage table."""
import sys
from pathlib import Path

from dotenv import load_dotenv


from klartext.adapters.llm import get_client
from klartext.adapters.pdf import extract_text
from klartext.services.pipeline import analyze_letter

load_dotenv("../.env")
model = sys.argv[1] if len(sys.argv) > 1 else "apertus-v1.5-8b"
client = get_client()

results = []
for pdf in sorted(Path("../data").glob("*.pdf")):
    text = extract_text(pdf.read_bytes())
    results.append(analyze_letter(client, model, pdf.stem, pdf.name, text))

# Same order as GET /letters: most urgent first, no deadline last.
results.sort(key=lambda r: (r.days_left is None, r.days_left or 0, -r.unverified_count))

print(f"{'letter':<28} {'type':<18} {'days left':<11} {'unverified':<11} {'ms':>6}")
for r in results:
    days = "-" if r.days_left is None else f"{'~' if r.days_left_estimated else ''}{r.days_left}"
    print(f"{r.filename:<28} {r.extraction.document_type:<18} {days:<11} {r.unverified_count:<11} {r.latency_ms:>6}")

