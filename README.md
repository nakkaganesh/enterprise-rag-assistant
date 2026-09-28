# Enterprise RAG Assistant

An end-to-end **Enterprise Retrieval-Augmented Generation (RAG) Assistant** for querying organizational documents using hybrid retrieval, reranking, grounded LLM generation, and evidence-based citations.

The system supports **TXT, PDF, and DOCX** documents and provides a FastAPI backend with a Streamlit chat interface.

---

## Features

- Multi-format document ingestion: TXT, PDF, DOCX
- Recursive multi-document loading
- Configurable text chunking with overlap
- Metadata preservation
- OpenAI embeddings
- FAISS semantic vector search
- BM25 keyword retrieval
- Hybrid retrieval
- Reciprocal Rank Fusion (RRF)
- LLM-based reranking
- Grounded answer generation
- Evidence-based citations
- Refusal when supporting information is unavailable
- Persistent FAISS vector index
- Automatic knowledge-base re-indexing
- Document upload API
- FastAPI REST backend
- Streamlit chat interface
- Automated RAG evaluation
- Environment-based configuration

---

## Architecture

```text
                     Enterprise Documents
                    TXT / PDF / DOCX
                           |
                           v
                  Document Ingestion
                           |
                           v
                  Chunking + Metadata
                           |
             +-------------+-------------+
             |                           |
             v                           v
      OpenAI Embeddings              BM25 Index
             |                           |
             v                           |
        FAISS Index                      |
             |                           |
             +-------------+-------------+
                           |
                           v
                    User Question
                           |
             +-------------+-------------+
             |                           |
             v                           v
      Semantic Search              Keyword Search
          FAISS                        BM25
             |                           |
             +-------------+-------------+
                           |
                           v
                Reciprocal Rank Fusion
                         (RRF)
                           |
                           v
                   Candidate Chunks
                           |
                           v
                      Reranker
                           |
                           v
                    Best Evidence
                           |
                           v
                Grounded LLM Generation
                           |
                           v
                Answer + Citations
                           |
                           v
                    FastAPI Backend
                           |
                           v
                   Streamlit Chat UI
```

---

## RAG Pipeline

### 1. Document Ingestion

Enterprise documents are loaded from the knowledge base.

Supported formats:

- `.txt`
- `.pdf`
- `.docx`

### 2. Chunking

Documents are divided into smaller overlapping chunks.

Metadata such as the source document and chunk identifier is preserved for retrieval and citation.

### 3. Embeddings

Chunks are converted into vector representations using OpenAI embeddings.

### 4. FAISS Semantic Retrieval

FAISS searches for chunks that are semantically similar to the user's question.

### 5. BM25 Keyword Retrieval

BM25 provides lexical retrieval for exact words, identifiers, policy numbers, and other keyword-sensitive queries.

For example:

```text
SEC-2026-101
```

### 6. Hybrid Search

FAISS and BM25 results are combined to benefit from both semantic and lexical retrieval.

### 7. Reciprocal Rank Fusion

RRF combines the independent FAISS and BM25 rankings without directly comparing their incompatible raw scores.

### 8. Reranking

The highest-ranked retrieval candidates are evaluated again for relevance to the user's question.

### 9. Grounded Generation

The LLM receives the question together with the selected document evidence and is instructed to answer only from that context.

If the answer is unavailable, the assistant responds:

```text
I could not find this information in the provided documents.
```

### 10. Evidence-Based Citations

Only chunks that directly support the generated answer are returned as citations.

Example:

```text
Question:
What authentication is required under SEC-2026-101?

Answer:
Multi-factor authentication is required for all employees using company systems.

Citation:
security_policy.txt — Chunk 0
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| Package Management | uv |
| LLM / Embeddings | OpenAI |
| Vector Search | FAISS |
| Keyword Search | BM25 |
| Rank Fusion | Reciprocal Rank Fusion |
| Backend | FastAPI |
| API Server | Uvicorn |
| Frontend | Streamlit |
| PDF Processing | PyPDF |
| DOCX Processing | python-docx |
| Testing | Pytest |
| HTTP Client | Requests |

---

## Project Structure

```text
enterprise-rag-assistant/
│
├── data/
│   ├── raw/
│   ├── evaluation/
│   └── vector_store/
│
├── src/
│   └── enterprise_rag/
│       ├── api/
│       ├── chunking/
│       ├── core/
│       ├── embeddings/
│       ├── evaluation/
│       ├── generation/
│       ├── ingestion/
│       ├── retrieval/
│       └── ui/
│
├── tests/
├── app.py
├── pyproject.toml
├── requirements.txt
├── uv.lock
├── .python-version
├── .gitignore
└── README.md
```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/nakkaganesh/enterprise-rag-assistant.git
cd enterprise-rag-assistant
```

### Install dependencies with uv

```bash
uv sync
```

---

## Environment Variables

Create a `.env` file or export the required environment variables.

The OpenAI client requires:

```text
OPENAI_API_KEY=your_api_key
```

Optional configuration:

```text
DATA_DIRECTORY=data/raw
VECTOR_STORE_DIRECTORY=data/vector_store
RAG_API_URL=http://127.0.0.1:8000
```

Never commit API keys or `.env` files to Git.

---

## Run the FastAPI Backend

```bash
uv run python -m uvicorn enterprise_rag.api.main:app --reload
```

The API runs locally on port `8000` by default.

### Health Check

```bash
curl http://127.0.0.1:8000/health
```

Example response:

```json
{
  "status": "ok"
}
```

---

## Ask Questions Through the API

```bash
curl -X POST \
  http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How many days per week can employees work remotely?"}'
```

Example response:

```json
{
  "question": "How many days per week can employees work remotely?",
  "answer": "Employees can work remotely up to three days per week.",
  "citations": [
    {
      "source": "remote_work_policy.txt",
      "page": null,
      "chunk_id": 0
    }
  ]
}
```

---

## Document Upload

Documents can be uploaded through the API.

```bash
curl -X POST \
  http://127.0.0.1:8000/documents/upload \
  -F "file=@policy.pdf"
```

The system:

```text
Upload
  ↓
Validate document
  ↓
Store document
  ↓
Load and chunk knowledge base
  ↓
Generate embeddings
  ↓
Rebuild FAISS
  ↓
Rebuild BM25
  ↓
Document becomes searchable
```

Supported uploads:

- TXT
- PDF
- DOCX

---

## Run the Streamlit Interface

Keep the FastAPI backend running and start Streamlit in another terminal:

```bash
uv run python -m streamlit run src/enterprise_rag/ui/app.py
```

The UI provides:

- Chat-based document Q&A
- Source citations
- Document upload
- Automatic indexing

---

## Evaluation

The project contains an automated evaluation pipeline covering:

- Answer correctness
- Citation correctness
- Unknown-question refusal

Run:

```bash
uv run python -m enterprise_rag.evaluation.evaluator
```

Current controlled evaluation set:

```text
Answer accuracy:    6/6
Citation accuracy:  6/6
Unknown refusal:    1/1
```

These results represent the included small controlled evaluation dataset and should not be interpreted as general 100% RAG accuracy.

---

## Testing

Run the automated tests:

```bash
uv run python -m pytest
```

Current test suite:

```text
4 passed
```

The tests cover core document loading, chunking, and ingestion functionality.

---

## Vector Store Persistence

The FAISS index and associated chunk metadata can be persisted locally.

```text
data/vector_store/
├── index.faiss
└── chunks.json
```

This prevents document embeddings from being regenerated every time the application starts.

Generated vector-store files are excluded from Git.

---

## Example Use Cases

The architecture can be adapted for:

- Employee policy assistants
- Internal knowledge bases
- HR document Q&A
- Technical documentation assistants
- Compliance knowledge systems
- Customer-support knowledge bases
- Research-document assistants

---

## Future Improvements

Potential production-scale improvements include:

- Incremental document indexing
- Authentication and authorization
- Multi-user document collections
- Background ingestion jobs
- Retrieval and generation observability
- Larger evaluation datasets
- Semantic caching
- Managed vector databases
- Cloud deployment
- CI/CD
- Containerization with Docker

---

## Author

**Ganesh Nakka**

AI / ML & Generative AI Engineer

GitHub: `nakkaganesh`

---

## Disclaimer

This project is an educational and portfolio implementation of an enterprise-style RAG architecture. Production deployments would require additional security, scalability, monitoring, access control, and evaluation measures.