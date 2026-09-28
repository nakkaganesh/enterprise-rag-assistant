import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "text-embedding-3-small"


class Embedder:

    def __init__(self):

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")

        self.client = OpenAI(api_key=api_key)

    def embed_documents(self,texts: list[str]) -> list[list[float]]:

        response = self.client.embeddings.create(
            model=MODEL_NAME,
            input=texts,
        )

        return [item.embedding for item in response.data]

    def embed_query(self,query: str) -> list[float]:

        response = self.client.embeddings.create(
            model=MODEL_NAME,
            input=query,
        )

        return response.data[0].embedding