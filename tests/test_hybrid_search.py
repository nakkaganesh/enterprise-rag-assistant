from enterprise_rag.embeddings.embedder import (
    Embedder,
)

from enterprise_rag.ingestion.pipeline import (
    prepare_chunks,
)

from enterprise_rag.retrieval.vector_store import (
    VectorStore,
)

from enterprise_rag.retrieval.bm25_search import (
    BM25Search,
)

from enterprise_rag.retrieval.hybrid_search import (
    HybridSearch,
)


# Prepare chunks
chunks = prepare_chunks(
    "data/raw",
    chunk_size=30,
    overlap=5,
)


# Embeddings
embedder = Embedder()

texts = [
    chunk["text"]
    for chunk in chunks
]

embeddings = embedder.embed_documents(
    texts
)


# FAISS
vector_store = VectorStore()

vector_store.add(
    chunks,
    embeddings,
)


# BM25
bm25 = BM25Search()

bm25.add(chunks)


# Hybrid
hybrid = HybridSearch(
    vector_store,
    bm25,
    embedder,
)


query = (
    "What authentication is required "
    "under SEC-2026-101?"
)

results = hybrid.search(
    query,
    top_k=3,
)


print("\nQUERY:")
print(query)

print("\nHYBRID RESULTS:")

for result in results:

    print(
        f"\nRRF: "
        f"{result['rrf_score']:.6f}"
    )

    print(
        f"Source: {result['source']}"
    )

    print(
        f"Chunk: {result['chunk_id']}"
    )

    print(
        f"Text: {result['text']}"
    )