from pathlib import Path
import os
import re
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
        data_directory: str = "data/raw",
        vector_store_directory: str = "data/vector_store",
    ):
        self.data_directory = data_directory
        self.store_path = Path(vector_store_directory)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self._index_lock = threading.RLock()

        self.embedder = Embedder()
        self.vector_store = VectorStore()
        self.reranker = Reranker()
        self.generator = AnswerGenerator()

        current = self.store_path / "CURRENT"
        legacy_index = self.store_path / "index.faiss"
        legacy_chunks = self.store_path / "chunks.json"

        if current.exists():
            version = current.read_text(encoding="utf-8").strip()
            if not re.fullmatch(r"[0-9a-f]{32}", version):
                raise ValueError("Invalid saved index version")
            location = self.store_path / "versions" / version
            print(f"Loading saved vector store version {version}...")
            self.vector_store.load(str(location))
            self.chunks = self.vector_store.chunks
        elif legacy_index.exists() and legacy_chunks.exists():
            print("Loading legacy saved vector store...")
            self.vector_store.load(str(self.store_path))
            self.chunks = self.vector_store.chunks
        else:
            print("No saved vector store; building initial index...")
            self.chunks = []
            self.rebuild_index()

        self._setup_retrieval()

    def _setup_retrieval(self):
        self.bm25 = BM25Search()
        self.bm25.add(self.chunks)
        self.hybrid = HybridSearch(self.vector_store, self.bm25, self.embedder)

    def _detect_source(self, query: str):
        query_folded = query.casefold()
        sources = {str(c.get("source", "")) for c in self.chunks if c.get("source")}
        for source in sorted(sources, key=len, reverse=True):
            filename = Path(source).name
            if source.casefold() in query_folded or filename.casefold() in query_folded:
                return source
        return None

    @staticmethod
    def _is_project_list_query(query: str) -> bool:
        q = query.casefold()
        return "project" in q and any(
            phrase in q
            for phrase in ("list", "all", "mentioned", "what are", "which", "names", "show")
        )

    @staticmethod
    def _chunk_order(chunk, fallback: int):
        value = chunk.get("chunk_id")
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return fallback

    def _project_section_chunks(self, document_chunks):
        """Collect resume project sections, keeping titles and details together."""
        start_headings = {"PROJECTS", "PERSONAL PROJECTS", "SELECTED PROJECTS", "KEY PROJECTS"}
        stop_headings = {
            "EDUCATION", "EDUCATION & CERTIFICATIONS", "CERTIFICATIONS",
            "TECHNICAL SKILLS", "PROFESSIONAL EXPERIENCE", "WORK EXPERIENCE",
            "PROFESSIONAL SUMMARY", "ACHIEVEMENTS", "AWARDS", "PUBLICATIONS",
            "CONTACT", "SKILLS", "INTERNSHIPS",
        }
        selected = []
        inside = False
        for chunk in document_chunks:
            heading = re.sub(r"\s+", " ", chunk.get("text", "").strip()).upper()
            if heading in start_headings:
                inside = True
                selected.append(chunk)
            elif heading in stop_headings:
                inside = False
            elif inside:
                selected.append(chunk)
        return selected

    def ask(self, query: str) -> dict:
        with self._index_lock:
            source = self._detect_source(query)

            if source:
                document_chunks = [c for c in self.chunks if c.get("source") == source]
                document_chunks = [
                    chunk for _, chunk in sorted(
                        enumerate(document_chunks),
                        key=lambda pair: self._chunk_order(pair[1], pair[0]),
                    )
                ]
                if self._is_project_list_query(query):
                    section_chunks = self._project_section_chunks(document_chunks)
                    # Include full sections when they fit a reasonable context budget.
                    # For large sections, use reranking to limit request size.
                    total_chars = sum(len(c.get("text", "")) for c in section_chunks)
                    if section_chunks and total_chars <= 24000:
                        best_chunks = section_chunks
                    else:
                        pool = section_chunks or document_chunks
                        best_chunks = self.reranker.rerank(
                            query, pool, top_k=min(12, len(pool))
                        )
                else:
                    best_chunks = self.reranker.rerank(
                        query, document_chunks, top_k=min(8, len(document_chunks))
                    )
            else:
                candidates = self.hybrid.search(query, top_k=20)
                best_chunks = self.reranker.rerank(
                    query, candidates, top_k=min(8, len(candidates))
                )

            if not best_chunks:
                return {"question": query, "answer": "No relevant document content found.", "citations": []}

            generation = self.generator.generate(query, best_chunks)
            citations = []
            seen = set()
            for index in generation.get("citations", []):
                if isinstance(index, int) and not isinstance(index, bool) and 0 <= index < len(best_chunks):
                    chunk = best_chunks[index]
                    citation = {
                        "source": chunk.get("source"),
                        "page": chunk.get("page"),
                        "chunk_id": chunk.get("chunk_id"),
                    }
                    key = (citation["source"], citation["page"], citation["chunk_id"])
                    if key not in seen:
                        seen.add(key)
                        citations.append(citation)
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
            data_directory = data_directory or self.data_directory
            if (
                vector_store_directory is not None
                and Path(vector_store_directory).resolve() != self.store_path.resolve()
            ):
                raise ValueError("Changing vector store directory is unsupported")

            chunks = prepare_chunks(data_directory, chunk_size=100, overlap=20)
            if not chunks:
                raise ValueError("No extractable document text found")

            embeddings = self.embedder.embed_documents([c["text"] for c in chunks])
            new_store = VectorStore()
            new_store.add(chunks, embeddings)
            new_bm25 = BM25Search()
            new_bm25.add(chunks)
            new_hybrid = HybridSearch(new_store, new_bm25, self.embedder)

            versions_dir = self.store_path / "versions"
            versions_dir.mkdir(parents=True, exist_ok=True)
            version = uuid.uuid4().hex
            version_dir = versions_dir / version
            version_dir.mkdir()
            new_store.save(str(version_dir))

            verified = VectorStore()
            verified.load(str(version_dir))
            if verified.index.ntotal != len(chunks):
                raise RuntimeError("Saved FAISS index verification failed")

            # Both pointer files are inside the same mounted directory.
            pointer_temp = self.store_path / f".CURRENT.{version}"
            with pointer_temp.open("w", encoding="utf-8") as handle:
                handle.write(version)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(pointer_temp, self.store_path / "CURRENT")

            self.vector_store = new_store
            self.chunks = chunks
            self.bm25 = new_bm25
            self.hybrid = new_hybrid
            print(f"FAISS index updated: {version}")
            return {"status": "success", "chunks": len(chunks), "index_version": version}
