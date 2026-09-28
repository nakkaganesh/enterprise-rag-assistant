from enterprise_rag.embeddings.embedder import Embedder


def dot_product(a, b):
    return sum(x * y for x, y in zip(a, b))


embedder = Embedder()

documents = [
    "Employees may work remotely.",
    "Employees receive paid vacation.",
]

document_vectors = embedder.embed_documents(
    documents
)

query_vector = embedder.embed_query(
    "Can employees work from home?"
)


for text, vector in zip(
    documents,
    document_vectors,
):
    score = dot_product(
        query_vector,
        vector,
    )

    print(
        f"{score:.4f} | {text}"
    )