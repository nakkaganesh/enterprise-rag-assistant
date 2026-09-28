from enterprise_rag.embeddings.embedder import Embedder
from enterprise_rag.ingestion.pipeline import prepare_chunks
from enterprise_rag.retrieval.bm25_search import BM25Search
from enterprise_rag.retrieval.hybrid_search import HybridSearch
from enterprise_rag.retrieval.reranker import Reranker
from enterprise_rag.retrieval.vector_store import VectorStore


chunks = prepare_chunks(
    "data/raw",
    chunk_size=30,
    overlap=5,
)

embedder = Embedder()

embeddings = embedder.embed_documents(
    [chunk["text"] for chunk in chunks]
)

vector_store = VectorStore()

vector_store.add(
    chunks,
    embeddings,
)

bm25 = BM25Search()
bm25.add(chunks)

hybrid = HybridSearch(
    vector_store,
    bm25,
    embedder,
)


query = "How many paid annual leave days do employees receive?"

candidates = hybrid.search(
    query,
    top_k=10,
)

reranker = Reranker()

results = reranker.rerank(
    query,
    candidates,
    top_k=3,
)


print("\nQUESTION:")
print(query)

print("\nRERANKED RESULTS:")

for result in results:

    print(
        f"\nScore: {result['rerank_score']}"
    )

    print(
        f"Source: {result['source']}"
    )

    print(
        f"Text: {result['text']}"
    )