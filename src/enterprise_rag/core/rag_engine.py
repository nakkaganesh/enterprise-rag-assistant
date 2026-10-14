from pathlib import Path


from enterprise_rag.embeddings.embedder import Embedder
from enterprise_rag.generation.generator import AnswerGenerator
from enterprise_rag.ingestion.pipeline import prepare_chunks
from enterprise_rag.retrieval.bm25_search import BM25Search
from enterprise_rag.retrieval.hybrid_search import HybridSearch
from enterprise_rag.retrieval.reranker import Reranker
from enterprise_rag.retrieval.vector_store import VectorStore


class RAGEngine:

    def __init__(
        self,
        data_directory: str = "data/raw",
        vector_store_directory: str = "data/vector_store",
    ):
        self.embedder = Embedder()
        self.vector_store = VectorStore()

        store_path = Path(vector_store_directory)

        index_exists = (
            (store_path / "index.faiss").exists()
            and (store_path / "chunks.json").exists()
        )

        if index_exists:
            print("Loading saved vector store...")

            self.vector_store.load(
                vector_store_directory
            )

            self.chunks = self.vector_store.chunks

        else:
            print("Building new vector store...")

            self.chunks = prepare_chunks(
                data_directory,
                chunk_size=100,
                overlap=20,
            )

            texts = [
                chunk["text"]
                for chunk in self.chunks
            ]

            if not texts:
                raise ValueError("No extractable text found in data/raw")

            embeddings = self.embedder.embed_documents(
                texts
            )

            self.vector_store.add(
                self.chunks,
                embeddings,
            )

            self.vector_store.save(
                vector_store_directory
            )

        self.bm25 = BM25Search()
        self.bm25.add(self.chunks)

        self.hybrid = HybridSearch(
            self.vector_store,
            self.bm25,
            self.embedder,
        )

        self.reranker = Reranker()
        self.generator = AnswerGenerator()

    def ask(
        self,
        query: str,
    ) -> dict:

        candidates = self.hybrid.search(
            query,
            top_k=10,
        )

        best_chunks = self.reranker.rerank(
            query,
            candidates,
            top_k=3,
        )

        generation = self.generator.generate(
            query,
            best_chunks,
        )

        citations = []

        for index in generation["citations"]:

            if 0 <= index < len(best_chunks):

                chunk = best_chunks[index]

                citations.append(
                    {
                        "source": chunk["source"],
                        "page": chunk.get("page"),
                        "chunk_id": chunk.get("chunk_id"),
                    }
                )

        return {
            "question": query,
            "answer": generation["answer"],
            "citations": citations,
        }
    def rebuild_index(
        self,
        data_directory: str = "data/raw",
        vector_store_directory: str = "data/vector_store",
    ) -> dict:
        """Build a new index before switching the live retrieval objects."""
        chunks = prepare_chunks(data_directory, chunk_size=100, overlap=20)
        if not chunks:
            raise ValueError("No extractable text found in the documents")

        embeddings = self.embedder.embed_documents(
            [chunk["text"] for chunk in chunks]
        )
        new_store = VectorStore()
        new_store.add(chunks, embeddings)
        new_bm25 = BM25Search()
        new_bm25.add(chunks)
        new_hybrid = HybridSearch(new_store, new_bm25, self.embedder)

        # Persist to temporary files before replacing saved index files.
        import os
        import tempfile
        store_path = Path(vector_store_directory)
        store_path.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=store_path.parent) as tmp:
            new_store.save(tmp)
            for name in ("index.faiss", "chunks.json"):
                os.replace(Path(tmp) / name, store_path / name)

        self.chunks = chunks
        self.vector_store = new_store
        self.bm25 = new_bm25
        self.hybrid = new_hybrid
        return {"status": "success", "chunks": len(chunks)}
