from fastapi import FastAPI
from pydantic import BaseModel

from enterprise_rag.core.rag_engine import RAGEngine


from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile


app = FastAPI(
    title="Enterprise RAG Assistant",
    version="1.0.0",
)

rag = RAGEngine()


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/ask")
def ask(request: QuestionRequest):

    result = rag.ask(
        request.question
    )

    return result
ALLOWED_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".docx",
}

DATA_DIRECTORY = Path("data/raw")


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
):
    filename = Path(file.filename).name

    extension = Path(
        filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Only TXT, PDF, and DOCX are allowed."
            ),
        )

    DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = (
        DATA_DIRECTORY / filename
    )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    destination.write_bytes(content)

    try:
        result = rag.rebuild_index()

    except Exception as error:
        # Remove the uploaded file if indexing failed.
        destination.unlink(
            missing_ok=True
        )

        raise HTTPException(
            status_code=500,
            detail=f"Indexing failed: {error}",
        )

    return {
        "message": "Document uploaded and indexed.",
        "filename": filename,
        "chunks": result["chunks"],
    }