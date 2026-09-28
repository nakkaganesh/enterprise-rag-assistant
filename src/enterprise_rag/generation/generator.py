import json

from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI


class AnswerGenerator:

    def __init__(self):
        self.client = OpenAI()

    def generate(
        self,
        query: str,
        chunks: list[dict],
    ) -> dict:

        context = "\n\n".join(
            f"[CHUNK {i}]\n"
            f"Source: {chunk['source']}\n"
            f"{chunk['text']}"
            for i, chunk in enumerate(chunks)
        )

        prompt = f"""
You are an enterprise knowledge assistant.

Answer the question using ONLY the provided context.

Return ONLY valid JSON in this format:

{{
  "answer": "your answer",
  "citations": [0]
}}

The citations list must contain ONLY the chunk numbers
that directly support the answer.

If the answer is not available in the context, return:

{{
  "answer": "I could not find this information in the provided documents.",
  "citations": []
}}

Do not invent information.

QUESTION:
{query}

CONTEXT:
{context}
"""

        response = self.client.responses.create(
            model="gpt-5.6-luna",
            input=prompt,
        )

        return json.loads(
            response.output_text
        )