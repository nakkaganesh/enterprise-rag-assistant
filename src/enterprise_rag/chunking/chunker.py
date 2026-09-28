
def chunk_text(text: str,chunk_size: int = 100,overlap: int = 20) -> list[str]:
    """Split text into overlapping word chunks."""


    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk_words = words[start:end]

        chunk = " ".join(chunk_words)

        chunks.append(chunk)

        start = end - overlap

    return chunks


def chunk_document(document: dict,chunk_size: int = 100,overlap: int = 20,) -> list[dict]:
    """Chunk a document while preserving metadata."""

    
    text_chunks = chunk_text(
        document["text"],
        chunk_size,
        overlap,
    )

    chunks = []

    for index, text in enumerate(text_chunks):

        chunk = document.copy()

        chunk["text"] = text
        chunk["chunk_id"] = index

        chunks.append(chunk)

    return chunks