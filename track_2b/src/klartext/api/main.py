import os
import uuid
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import openai
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import ValidationError

from klartext.adapters.llm import LLMConfigError, get_client
from klartext.adapters.pdf import EmptyDocumentError, extract_text
from klartext.domain.models import LetterResult
from klartext.services.explainer import LANGUAGES, explain
from klartext.services.pipeline import analyze_letter, analyze_with_cascade

app = FastAPI(title="Klartext")

@app.exception_handler(LLMConfigError)
async def llm_not_configured(request, exc: LLMConfigError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(openai.OpenAIError)
async def llm_unavailable(request, exc: openai.OpenAIError):
    return JSONResponse(status_code=502, content={"detail": f"The language model endpoint failed: {exc}"})

DEFAULT_MODEL = os.environ.get("LLM_NAME") or "apertus-v1.5-8b"
LARGE_MODEL = os.environ.get("LLM_NAME_LARGE") or "apertus-v1.5-70b"


@dataclass
class StoredDocument:
    filename: str
    text: str


# In-memory stores: letters and results are never written to disk (privacy by design).
documents: dict[str, StoredDocument] = {}
results: dict[str, LetterResult] = {}


@lru_cache
def client() -> OpenAI:
    """One shared LLM client, created on first use."""
    return get_client()


async def _store(file: UploadFile) -> tuple[str, str]:
    """Validate a PDF upload, extract its text and keep it in memory. Returns (id, text)."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Only PDF files are supported.")
    try:
        text = extract_text(await file.read())
    except EmptyDocumentError as e:
        raise HTTPException(status_code=422, detail=str(e))

    doc_id = str(uuid.uuid4())
    documents[doc_id] = StoredDocument(filename=file.filename or "letter.pdf", text=text)
    return doc_id, text


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/documents", status_code=201)
async def upload_document(file: UploadFile):
    doc_id, text = await _store(file)
    return {"id": doc_id, "filename": file.filename, "text": text}


@app.post("/documents/batch", status_code=201)
async def upload_batch(files: list[UploadFile]):
    """Upload several letters at once; one bad file does not stop the others."""
    uploaded, failed = [], []
    for file in files:
        try:
            doc_id, _ = await _store(file)
            uploaded.append({"id": doc_id, "filename": file.filename})
        except HTTPException as e:
            failed.append({"filename": file.filename, "error": e.detail})
    return {"uploaded": uploaded, "failed": failed}

@app.post("/documents/{doc_id}/extract", response_model=LetterResult)
def extract_document(doc_id: str, model: str | None = None):
    doc = documents.get(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    try:
        if model:
            result = analyze_letter(client(), model, doc_id, doc.filename, doc.text)
        else:
            result = analyze_with_cascade(
                client(), DEFAULT_MODEL, LARGE_MODEL, doc_id, doc.filename, doc.text
            )
    except (ValueError, ValidationError) as e:
        raise HTTPException(status_code=502, detail=f"Model returned invalid output: {e}")
    results[doc_id] = result
    return result

@app.get("/letters", response_model=list[LetterResult])
def list_letters():
    """Triage view: most urgent letters first, letters without a deadline last."""
    return sorted(
        results.values(),
        key=lambda r: (r.days_left is None, r.days_left or 0, -r.unverified_count),
    )


@app.post("/documents/{doc_id}/explain", response_model=LetterResult)
def explain_document(doc_id: str, language: str = "en", model: str = LARGE_MODEL):
    """Explain an analysed letter in the client's language, using verified facts only."""
    result = results.get(doc_id)
    if result is None:
        raise HTTPException(status_code=409, detail="Analyse the letter first via /extract.")
    if language not in LANGUAGES:
        raise HTTPException(status_code=422, detail=f"Unsupported language. Use one of: {', '.join(LANGUAGES)}")
    result.explanation = explain(client(), model, result, language)
    return result

# The built UI is copied to /app/static by the Dockerfile; serve it last so API routes win.
STATIC_DIR = Path(__file__).resolve().parents[2] / "static"
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="ui")