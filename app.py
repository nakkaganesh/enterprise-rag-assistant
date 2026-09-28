from enterprise_rag.core.rag_engine import RAGEngine


print("Building knowledge base...")

rag = RAGEngine()

print("Enterprise RAG Assistant ready.")
print("\nType 'exit' to stop.")


while True:

    question = input(
        "\nAsk a question: "
    ).strip()

    if question.lower() == "exit":
        break

    if not question:
        continue

    result = rag.ask(question)

    print("\nANSWER:")
    print(result["answer"])

    print("\nCITATIONS:")

    if not result["citations"]:
        print("- None")

    else:
        for citation in result["citations"]:

            text = f"- {citation['source']}"

            if citation["page"] is not None:
                text += (
                    f", page {citation['page']}"
                )

            if citation["chunk_id"] is not None:
                text += (
                    f", chunk {citation['chunk_id']}"
                )

            print(text)