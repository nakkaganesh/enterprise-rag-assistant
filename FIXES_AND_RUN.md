# Fixes and local run instructions

## What changed
- Fixed DOCX ingestion (`paragraph.text.strip()`).
- Fixed word chunking so the last short chunk is not duplicated.
- Added predictable ingestion order and missing-directory handling.
- Added upload file validation (10 MB limit), rollback of an overwritten file on indexing failure, and detailed server-side exception logging.
- Rebuild now constructs replacement search objects before switching live references.
- Compose frontend now connects to `http://api:8000` rather than localhost inside its container.
- Removed the unused duplicate `src/enterprise_rag/ui/app.py` Streamlit interface; keep `frontend/app.py`.
- Removed unused `unicorn` dependency from pyproject.toml (the correct ASGI server is `uvicorn`).
- Changed backend health check to `/health`.

## Run locally (two terminals)

1. `uv sync` (requires network on your machine; sync may update uv.lock after pyproject changes)
2. `uv run uvicorn enterprise_rag.api.main:app --app-dir src --host 127.0.0.1 --port 8000`
3. `uv run streamlit run frontend/app.py --server.port 8501`
4. Open `http://localhost:8501` and upload a small TXT document first.

Check that your local `.env` contains `OPENAI_API_KEY`, without sharing it. If port 8000 is occupied, stop the previous backend rather than starting another. For Docker Compose: `docker compose up --build` (requires `.env` locally).

## Remaining caveats
- External OpenAI embeddings and LLM responses were not exercised in this offline environment. Check the FastAPI terminal traceback if uploads still fail.
- The OpenAI model IDs in reranker.py and generator.py were left unchanged; verify they are accessible to your account if `/ask` fails.
- The `uv.lock` and exported `requirements.txt` are original; regenerate both after changing dependencies: `uv lock && uv export --format requirements-txt --no-hashes --no-emit-project --output-file requirements.txt`.
- The in-memory RAG engine is not safe for concurrent uploads or multiple API workers; production deployments need a serialized index update and durable shared storage.
- Uploaded documents may be sensitive; add authentication and access control before exposing the upload API publicly.
