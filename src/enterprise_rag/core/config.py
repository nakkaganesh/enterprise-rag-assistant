import os


DATA_DIRECTORY = os.getenv(
    "DATA_DIRECTORY",
    "data/raw",
)

VECTOR_STORE_DIRECTORY = os.getenv(
    "VECTOR_STORE_DIRECTORY",
    "data/vector_store",
)

API_URL = os.getenv(
    "RAG_API_URL",
    "http://127.0.0.1:8000",
)