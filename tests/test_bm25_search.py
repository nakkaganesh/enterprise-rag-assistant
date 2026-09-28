from enterprise_rag.ingestion.pipeline import prepare_chunks

from enterprise_rag.retrieval.bm25_search import BM25Search


chunks = prepare_chunks(
    "data/raw",
    chunk_size=30,
    overlap=5,
)

search = BM25Search()

search.add(chunks)

query = "SEC-2026-101"

results = search.search(
    query,
    top_k=3,
)


print("\nQUERY:")
print(query)

print("\nBM25 RESULTS:")

for result in results:

    print(
        f"\nScore: "
        f"{result['bm25_score']:.4f}"
    )

    print(
        f"Source: {result['source']}"
    )

    print(
        f"Text: {result['text']}"
    )