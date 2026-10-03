from fastapi import FastAPI

app = FastAPI(title="Klartext")


@app.get("/health")
def health():
    return {"status": "ok"}