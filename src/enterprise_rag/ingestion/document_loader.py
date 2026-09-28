from pathlib import Path

from enterprise_rag.ingestion.text_loader import load_txt
from enterprise_rag.ingestion.pdf_loader import load_pdf
from enterprise_rag.ingestion.docx_loader import load_docx

def load_document(file_path : str | Path)->list[dict]:
    "load a supported document"

    path=Path(file_path)

    suffix=path.suffix.lower()

    if suffix == ".txt":
        return load_txt(path)
    if suffix == ".pdf":
        return load_pdf(path)
    if suffix == ".docx":
        return load_docx(path)

    raise ValueError(f"unsupported file:{suffix}")