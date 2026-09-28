from enterprise_rag.generation.generator import (
    AnswerGenerator,
)


query = (
    "How many paid annual leave days "
    "do full-time employees receive?"
)


chunks = [
    {
        "text": (
            "Full-time employees receive "
            "20 days of paid annual leave "
            "per calendar year."
        ),
        "source": "leave_policy.txt",
    }
]


generator = AnswerGenerator()

answer = generator.generate(
    query,
    chunks,
)


print("\nQUESTION:")
print(query)

print("\nANSWER:")
print(answer)