# Local RAG POC

Two FastAPI endpoints over a local vector store:

- **Ingestion** — accepts a local PDF path, chunks and embeds it, stores it in ChromaDB on disk.
- **Query** — takes a question, retrieves the top-k chunks, and asks Gemini for a grounded answer.

## Quick start (fresh Mac, nothing installed)

Open Terminal and run:

```bash
curl -fsSL https://raw.githubusercontent.com/anandptl84/local-rag-poc/main/setup.sh | bash
```

The script installs Homebrew, Python, and the GitHub CLI, logs you in to GitHub,
clones this repo to `~/local-rag-poc`, sets up the virtualenv and `.env`, and
starts the server. You'll need a [Gemini API key](https://aistudio.google.com/apikey)
when prompted (or add it to `.env` later). Safe to re-run at any time.

## Manual start (already set up)

```bash
cd ~/local-rag-poc
./venv/bin/uvicorn app.main:app --reload
```

- API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## Contributing

`main` is protected — work on a branch and open a pull request:

```bash
git checkout -b feature/my-change
# ...edit, commit...
git push -u origin feature/my-change
gh pr create
```

Every PR needs one approving review before it can merge.
