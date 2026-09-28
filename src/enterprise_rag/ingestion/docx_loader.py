from pathlib import Path
from docx import Document

def load_docx(file_path:str | Path)-> list[dict]:
    "load paragraph from a docx file"

    path=Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    document=Document(path)

    documents=[]

    for paragraph_number,paragraph in enumerate(document.paragraphs,start=1):

        text=paragraph.strip()

        if not text:
            continue

        documents.append(
            {
                "text": text,
                "source": path.name,
                "file_type": "docx",
                "page": None,
                "paragraph": paragraph_number,
            }
        )

    return documents