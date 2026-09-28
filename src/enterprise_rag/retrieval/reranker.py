import json

from openai import OpenAI


class Reranker:

    def __init__(self):
        self.client = OpenAI()

    def rerank(
        self,
        query: str,
        chunks: list[dict],
        top_k: int = 3,
    ) -> list[dict]:

        if not chunks:
            return []

        numbered_chunks = "\n\n".join(
            f"CHUNK {i}:\n{chunk['text']}"
            for i, chunk in enumerate(chunks)
        )

        prompt = f"""
You are a relevance reranker.

Question:
{query}

Candidate chunks:
{numbered_chunks}

Score every chunk from 0 to 10 based only on
how useful it is for answering the question.

Return ONLY valid JSON in this format:

[
  {{"index": 0, "score": 9.5}},
  {{"index": 1, "score": 3.0}}
]
"""

        response = self.client.responses.create(
            model="gpt-5.6-luna",
            input=prompt,
        )

        rankings = json.loads(
            response.output_text
        )

        rankings.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        results = []

        for item in rankings[:top_k]:

            index = item["index"]

            result = chunks[index].copy()

            result["rerank_score"] = float(
                item["score"]
            )

            results.append(result)

        return results