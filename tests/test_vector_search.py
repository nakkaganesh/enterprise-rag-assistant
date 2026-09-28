from enterprise_rag.embeddings.embedder import Embedder
from enterprise_rag.ingestion.pipeline import prepare_chunks
from enterprise_rag.retrieval.vector_store import VectorStore


chunks = prepare_chunks(
    "data/raw",
    chunk_size=20,
    overlap=5,
)

texts = [
    chunk["text"]
    for chunk in chunks
]

embedder = Embedder()

embeddings = embedder.embed_documents(
    texts
)

store = VectorStore()

store.add(
    chunks,
    embeddings,
)

query = "Can employees work remotely?"

query_embedding = embedder.embed_query(
    query
)

results = store.search(
    query_embedding,
    top_k=3,
)


print("\nQUERY:")
print(query)

print("\nRESULTS:")

for result in results:

    print(
        f"\nScore: {result['score']:.4f}"
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