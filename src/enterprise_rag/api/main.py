import logging
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from enterprise_rag.core.rag_engine import RAGEngine

logger = logging.getLogger(__name__)
app = FastAPI(title="Enterprise RAG Assistant", version="1.0.1")
rag = RAGEngine()
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}
DATA_DIRECTORY = Path("data/raw")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        return rag.ask(request.question)
    except Exception:
        logger.exception("Question answering failed")
        raise HTTPException(status_code=500, detail="Question answering failed; check API logs")


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()
    if not filename or extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only TXT, PDF, and DOCX files are allowed")

    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 10 MB upload limit")

    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = DATA_DIRECTORY / filename
    previous_content = destination.read_bytes() if destination.exists() else None
    destination.write_bytes(content)
    try:
        result = rag.rebuild_index()
    except Exception:
        logger.exception("Document indexing failed for %s", filename)
        if previous_content is None:
            destination.unlink(missing_ok=True)
        else:
            destination.write_bytes(previous_content)
        raise HTTPException(status_code=500, detail="Indexing failed; check FastAPI terminal logs")

    return {"message": "Document uploaded and indexed.",
            "filename": filename, "chunks": result["chunks"]}
