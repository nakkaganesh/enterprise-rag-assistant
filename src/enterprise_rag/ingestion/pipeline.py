from pathlib import Path

from enterprise_rag.ingestion.document_loader import load_document
from enterprise_rag.chunking.chunker import chunk_document

def ingest_directory(directory):
    """Load all supported documents from a directory."""

    folder = Path(directory)

    all_documents = []

    for file_path in folder.iterdir():

        if file_path.suffix.lower() not in {
            ".txt",
            ".pdf",
            ".docx",
        }:
            continue

        documents = load_document(file_path)

        all_documents.extend(documents)

    return all_documents



def prepare_chunks(
    directory,
    chunk_size=100,
    overlap=20,
):
    """Load documents and convert them into chunks."""

    documents = ingest_directory(directory)

    all_chunks = []

    for document in documents:

        chunks = chunk_document(
            document,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        all_chunks.extend(chunks)

    return all_chunks