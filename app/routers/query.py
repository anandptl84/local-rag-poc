from fastapi import APIRouter, Depends

from ..config import settings
from ..deps import get_embedder, get_llm, get_vectorstore
from ..schemas import Citation, QueryRequest, QueryResponse
from ..services.embeddings import Embedder
from ..services.llm import LLMClient
from ..services.vectorstore import VectorStore

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query(
    req: QueryRequest,
    embedder: Embedder = Depends(get_embedder),
    store: VectorStore = Depends(get_vectorstore),
    llm: LLMClient = Depends(get_llm),
) -> QueryResponse:
    top_k = req.top_k or settings.top_k
    [query_embedding] = embedder.embed([req.question])
    hits = store.query(query_embedding, top_k)

    answer = llm.answer(req.question, hits)
    grounded = settings.refusal_message.strip() not in answer.strip()

    citations = (
        [
            Citation(
                source=h["metadata"]["source"],
                page=int(h["metadata"]["page"]),
                snippet=h["text"][:200],
            )
            for h in hits
        ]
        if grounded
        else []
    )

    return QueryResponse(answer=answer, grounded=grounded, citations=citations)
