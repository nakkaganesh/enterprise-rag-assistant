from pathlib import Path
from pypdf import PdfReader

def load_pdf(file_path:str | Path)->list[dict]:
    "load a pdf file while preserving meta data"

    path=Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"path not found{path}")

    reader=PdfReader(path)

    documents=[]

    for page_number,page in enumerate(reader.pages,start=1):

        text=page.extract_text()

        if not text:
            continue

        text=text.strip()

        if not text:
            continue


        documents.append(
            {
                "text": text,
                "source": path.name,
                "file_type": "pdf",
                "page": page_number,
            }
        )

    return documents