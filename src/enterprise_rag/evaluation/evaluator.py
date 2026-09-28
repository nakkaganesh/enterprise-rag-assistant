import json

from enterprise_rag.core.rag_engine import RAGEngine


NOT_FOUND = (
    "I could not find this information "
    "in the provided documents."
)


def load_questions(path):
    with open(path, "r") as file:
        return json.load(file)


def evaluate():

    questions = load_questions(
        "data/evaluation/questions.json"
    )

    print("Building RAG system...")

    rag = RAGEngine()

    answer_passes = 0
    citation_passes = 0
    refusal_passes = 0
    refusal_total = 0

    for item in questions:

        question = item["question"]

        print(f"\nQUESTION: {question}")

        result = rag.ask(question)

        answer = result["answer"]

        sources = [
            citation["source"]
            for citation in result["citations"]
        ]

        print(f"ANSWER: {answer}")
        print(f"CITATIONS: {sources}")

        if item["answerable"]:

            expected_answer = (
                item["expected_answer"].lower()
            )

            if expected_answer in answer.lower():
                answer_passes += 1
                print("Answer: PASS")
            else:
                print("Answer: FAIL")

            if item["expected_source"] in sources:
                citation_passes += 1
                print("Citation: PASS")
            else:
                print("Citation: FAIL")

        else:

            refusal_total += 1

            if (
                NOT_FOUND.lower()
                in answer.lower()
                and not sources
            ):
                refusal_passes += 1
                print("Refusal: PASS")
            else:
                print("Refusal: FAIL")

    answerable_total = sum(
        1
        for item in questions
        if item["answerable"]
    )

    print("\n======================")
    print("EVALUATION RESULTS")
    print("======================")

    print(
        f"Answer accuracy: "
        f"{answer_passes}/{answerable_total}"
    )

    print(
        f"Citation accuracy: "
        f"{citation_passes}/{answerable_total}"
    )

    print(
        f"Unknown refusal: "
        f"{refusal_passes}/{refusal_total}"
    )


if __name__ == "__main__":
    evaluate()