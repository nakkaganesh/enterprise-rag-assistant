from rank_bm25 import BM25Okapi


class BM25Search:

    def __init__(self):
        self.bm25 = None
        self.chunks = []

    def add(self,chunks: list[dict]):
        """Index chunks for keyword search."""

        self.chunks = chunks

        tokenized_chunks = [
            chunk["text"].lower().split()
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(tokenized_chunks)

    def search(self,query: str,top_k: int = 3) -> list[dict]:
        """Search chunks using BM25."""

        if self.bm25 is None:
            return []

        tokenized_query = (
            query.lower().split()
        )

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True,
        )[:top_k]

        results = []

        for index in ranked_indices:

            result = self.chunks[index].copy()

            result["bm25_score"] = float(
                scores[index]
            )

            results.append(result)

        return results