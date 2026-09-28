import json
from pathlib import Path
import faiss
import numpy as np


class VectorStore:

    def __init__(self):
        self.index = None
        self.chunks = []

    def add(self,chunks: list[dict],embeddings: list[list[float]]):
        """Add chunks and their vectors to FAISS."""

        vectors = np.array(embeddings,dtype="float32")

        dimension = vectors.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(vectors)

        self.chunks = chunks

    def search(self,query_embedding: list[float],top_k: int = 3) -> list[dict]:
        """Find the most similar chunks."""

        if self.index is None:
            return []

        query = np.array([query_embedding],dtype="float32",
        )

        scores, indices = self.index.search(query,top_k)

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index == -1:
                continue

            result = self.chunks[index].copy()

            result["score"] = float(score)

            results.append(result)

        return results
    def save(
    self,
    directory: str,
):
        """Save FAISS index and chunks."""

        if self.index is None:
            raise ValueError(
                "Vector store is empty"
            )

        directory = Path(directory)

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Save FAISS index
        faiss.write_index(
            self.index,
            str(directory / "index.faiss"),
        )

        # Save chunk text + metadata
        with open(
            directory / "chunks.json",
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self.chunks,
                file,
                indent=2,
            )


    def load(
        self,
        directory: str,
    ):
        """Load FAISS index and chunks."""

        directory = Path(directory)

        index_path = (
            directory / "index.faiss"
        )

        chunks_path = (
            directory / "chunks.json"
        )

        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {index_path}"
            )

        if not chunks_path.exists():
            raise FileNotFoundError(
                f"Chunks not found: {chunks_path}"
            )

        # Load FAISS index
        self.index = faiss.read_index(
            str(index_path)
        )

        # Load chunk text + metadata
        with open(
            chunks_path,
            "r",
            encoding="utf-8",
        ) as file:

            self.chunks = json.load(file)