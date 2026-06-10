from fastapi import FastAPI

from .routers import ingest, query

app = FastAPI(title="Local RAG POC")

app.include_router(ingest.router)
app.include_router(query.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
