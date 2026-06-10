from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from ..config import settings
from ..deps import get_embedder, get_vectorstore
from ..schemas import IngestRequest, IngestResponse
from ..services.chunking import chunk_text
from ..services.embeddings import Embedder
from ..services.pdf import extract_pages
from ..services.vectorstore import VectorStore

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
def ingest(
    req: IngestRequest,
    embedder: Embedder = Depends(get_embedder),
    store: VectorStore = Depends(get_vectorstore),
) -> IngestResponse:
    try:
        pages = extract_pages(req.path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not pages:
        raise HTTPException(status_code=400, detail="PDF contains no extractable text")

    source = Path(req.path).name
    ids: list[str] = []
    docs: list[str] = []
    metas: list[dict] = []

    chunk_idx = 0
    for page_num, page_text in pages:
        for chunk in chunk_text(page_text, settings.chunk_size, settings.chunk_overlap):
            ids.append(f"{source}::chunk_{chunk_idx}")
            docs.append(chunk)
            metas.append({"source": source, "page": page_num, "chunk_index": chunk_idx})
            chunk_idx += 1

    if not docs:
        raise HTTPException(status_code=400, detail="No chunks produced from PDF")

    embeddings = embedder.embed(docs)
    store.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)

    return IngestResponse(source=source, pages=len(pages), chunks_added=len(docs))
