from enterprise_rag.chunking.chunker import (
    chunk_document,
    chunk_text,
)


def test_chunk_text():
    text = "one two three four five six seven eight"

    chunks = chunk_text(
        text,
        chunk_size=4,
        overlap=1,
    )

    assert chunks[0] == "one two three four"

    assert chunks[1] == "four five six seven"


def test_chunk_document_preserves_metadata():

    document = {
        "text": "one two three four five six",
        "source": "policy.txt",
        "file_type": "txt",
        "page": None,
    }

    chunks = chunk_document(
        document,
        chunk_size=4,
        overlap=1,
    )

    assert chunks[0]["source"] == "policy.txt"
    assert chunks[0]["chunk_id"] == 0
    assert chunks[1]["chunk_id"] == 1