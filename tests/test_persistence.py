from enterprise_rag.embeddings.embedder import Embedder
from enterprise_rag.ingestion.pipeline import prepare_chunks
from enterprise_rag.retrieval.vector_store import VectorStore


chunks = prepare_chunks(
    "data/raw",
    chunk_size=100,
    overlap=20,
)

embedder = Embedder()

embeddings = embedder.embed_documents(
    [
        chunk["text"]
        for chunk in chunks
    ]
)


# Build and save
store = VectorStore()

store.add(
    chunks,
    embeddings,
)

store.save(
    "data/vector_store"
)

print("Vector store saved.")


# Create completely new store
new_store = VectorStore()

new_store.load(
    "data/vector_store"
)

print("Vector store loaded.")

print(
    "Chunks:",
    len(new_store.chunks),
)

print(
    "Vectors:",
    new_store.index.ntotal,
)