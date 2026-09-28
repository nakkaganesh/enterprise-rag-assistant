from enterprise_rag.ingestion.pipeline import ingest_directory


def test_ingest_directory():
    documents = ingest_directory("data/raw")

    assert len(documents) >= 1

    assert any(
        document["source"] == "remote_work_policy.txt"
        for document in documents
    )