class HybridSearch:

    def __init__(
        self,
        vector_store,
        bm25_search,
        embedder,
    ):
        self.vector_store = vector_store
        self.bm25_search = bm25_search
        self.embedder = embedder


    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:

        # Semantic retrieval
        query_embedding = (
            self.embedder.embed_query(query)
        )

        vector_results = (
            self.vector_store.search(
                query_embedding,
                top_k=top_k,
            )
        )

        # Keyword retrieval
        bm25_results = (
            self.bm25_search.search(
                query,
                top_k=top_k,
            )
        )

        return self._rrf(
            vector_results,
            bm25_results,
            top_k,
        )


    def _rrf(
        self,
        vector_results,
        bm25_results,
        top_k,
    ):

        scores = {}
        documents = {}

        # RRF constant
        k = 60

        result_lists = [
            vector_results,
            bm25_results,
        ]

        for results in result_lists:

            for rank, result in enumerate(
                results,
                start=1,
            ):

                key = (
                    result["source"],
                    result["chunk_id"],
                )

                rrf_score = 1 / (
                    k + rank
                )

                scores[key] = (
                    scores.get(key, 0)
                    + rrf_score
                )

                documents[key] = result

        ranked_keys = sorted(
            scores,
            key=scores.get,
            reverse=True,
        )

        final_results = []

        for key in ranked_keys[:top_k]:

            result = documents[key].copy()

            result["rrf_score"] = (
                scores[key]
            )

            final_results.append(result)

        return final_results