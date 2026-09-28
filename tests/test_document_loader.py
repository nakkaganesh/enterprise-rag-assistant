from enterprise_rag.ingestion.document_loader import load_document

def test_txt_loader():
    documents = load_document("data/raw/remote_work_policy.txt")

    assert len(documents) == 1

    document = documents[0]

    assert document["file_type"] == "txt"
    assert (document["source"]== "remote_work_policy.txt")

    assert "three days" in document["text"]