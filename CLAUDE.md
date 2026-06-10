# Local RAG POC

## Goal
Two Python APIs (FastAPI):
1. **Ingestion API** — accepts a local PDF path, chunks/embeds it, stores in a local vector DB.
2. **Query API** — takes a question, retrieves top-k chunks from the vector DB, and asks an LLM for a grounded answer.

## Stack
- Python 3.x, venv at ./venv
- FastAPI + uvicorn for the APIs
- Vector DB: <pick one — ChromaDB or FAISS for local; both run on disk with no server>
- Embeddings: <e.g., sentence-transformers/all-MiniLM-L6-v2, or OpenAI/Anthropic embeddings>
- LLM for generation: <Claude via the Anthropic SDK, or local via Ollama>
- PDF parsing: pypdf or pdfplumber

## Conventions
- Type hints everywhere
- Pydantic models for request/response schemas
- Keep ingestion and query as two separate FastAPI apps (or one app with two routers) per the brief
- Persist the vector store to ./data/ so it survives restarts
