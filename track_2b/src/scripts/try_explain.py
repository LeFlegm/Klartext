"""Manual check: analyse one letter with 8B, then explain it in several languages with 70B."""
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from klartext.adapters.llm import get_client
from klartext.adapters.pdf import extract_text
from klartext.services.explainer import explain
from klartext.services.pipeline import analyze_letter

load_dotenv("../.env")
pdf = Path(sys.argv[1] if len(sys.argv) > 1 else "../data/CH_BETREIBUNG_003_fr.pdf")
languages = sys.argv[2:] or ["tr", "en", "ti"]

client = get_client()
result = analyze_letter(client, "apertus-v1.5-8b", pdf.stem, pdf.name, extract_text(pdf.read_bytes()))

for language in languages:
    start = time.perf_counter()
    explanation = explain(client, "apertus-v1.5-70b", result, language)
    print(f"--- {language} ({time.perf_counter() - start:.1f}s)\n{explanation.text}\n")