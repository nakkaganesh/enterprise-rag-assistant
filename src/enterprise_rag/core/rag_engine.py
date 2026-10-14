
from pathlib import Path
import os
import threading
import uuid

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
        data_directory="data/raw",
        vector_store_directory="data/vector_store",
    ):
        self.data_directory = data_directory
        self.store_path = Path(vector_store_directory)
        self.store_path.mkdir(parents=True, exist_ok=True)

        self._index_lock = threading.RLock()

        self.embedder = Embedder()
        self.vector_store = VectorStore()
        self.reranker = Reranker()
        self.generator = AnswerGenerator()

        current_file = self.store_path / "CURRENT"

        if current_file.exists():
            version = current_file.read_text().strip()

            if not version or Path(version).name != version:
                raise ValueError("Invalid index version")

            index_path = self.store_path / "versions" / version

            self.vector_store.load(str(index_path))
            self.chunks = self.vector_store.chunks

        elif (
            (self.store_path / "index.faiss").exists()
            and (self.store_path / "chunks.json").exists()
        ):
            print("Loading existing FAISS index...")

            self.vector_store.load(str(self.store_path))
            self.chunks = self.vector_store.chunks

        else:
            print("Building initial FAISS index...")
            self.rebuild_index()

        self._setup_retrieval()

    def _setup_retrieval(self):
        self.bm25 = BM25Search()
        self.bm25.add(self.chunks)

        self.hybrid = HybridSearch(
            self.vector_store,
            self.bm25,
            self.embedder,
        )

    def ask(self, query: str) -> dict:

        with self._index_lock:
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

                    citations.append({
                        "source": chunk["source"],
                        "page": chunk.get("page"),
                        "chunk_id": chunk.get("chunk_id"),
                    })

            return {
                "question": query,
                "answer": generation["answer"],
                "citations": citations,
            }

    def rebuild_index(
        self,
        data_directory=None,
        vector_store_directory=None,
    ) -> dict:

        with self._index_lock:

            data_directory = (
                data_directory or self.data_directory
            )

            if (
                vector_store_directory is not None
                and Path(vector_store_directory).resolve()
                != self.store_path.resolve()
            ):
                raise ValueError(
                    "Changing vector store directory is unsupported"
                )

            chunks = prepare_chunks(
                data_directory,
                chunk_size=100,
                overlap=20,
            )

            if not chunks:
                raise ValueError("No extractable document text")

            embeddings = self.embedder.embed_documents(
                [chunk["text"] for chunk in chunks]
            )

            new_store = VectorStore()
            new_store.add(chunks, embeddings)

            new_bm25 = BM25Search()
            new_bm25.add(chunks)

            new_hybrid = HybridSearch(
                new_store,
                new_bm25,
                self.embedder,
            )

            versions_path = self.store_path / "versions"
            versions_path.mkdir(parents=True, exist_ok=True)

            version = uuid.uuid4().hex
            version_path = versions_path / version
            version_path.mkdir()

            new_store.save(str(version_path))

            # Verify saved index
            verified = VectorStore()
            verified.load(str(version_path))

            if verified.index.ntotal != len(chunks):
                raise RuntimeError(
                    "FAISS index validation failed"
                )

            # Publish index using a same-filesystem rename
            temp_pointer = self.store_path / f".CURRENT.{version}"
            current_pointer = self.store_path / "CURRENT"

            with open(temp_pointer, "w", encoding="utf-8") as f:
                f.write(version)
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp_pointer, current_pointer)

            # Activate new index
            self.vector_store = new_store
            self.chunks = chunks
            self.bm25 = new_bm25
            self.hybrid = new_hybrid

            print(f"FAISS index updated: {version}")

            return {
                "status": "success",
                "chunks": len(chunks),
                "index_version": version,
            }
