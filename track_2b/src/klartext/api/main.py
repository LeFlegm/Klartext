import uuid

from fastapi import FastAPI, HTTPException, UploadFile

from klartext.adapters.pdf import EmptyDocumentError, extract_text

app = FastAPI(title="Klartext")

# In-memory store: letters are never written to disk (privacy by design).
documents: dict[str, str] = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/documents", status_code=201)
async def upload_document(file: UploadFile):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Only PDF files are supported.")

    pdf_bytes = await file.read()
    try:
        text = extract_text(pdf_bytes)
    except EmptyDocumentError as e:
        raise HTTPException(status_code=422, detail=str(e))

    doc_id = str(uuid.uuid4())
    documents[doc_id] = text
    return {"id": doc_id, "filename": file.filename, "text": text}