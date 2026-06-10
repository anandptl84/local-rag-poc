from functools import lru_cache

from .config import settings
from .services.embeddings import Embedder
from .services.llm import LLMClient
from .services.vectorstore import VectorStore


@lru_cache
def get_embedder() -> Embedder:
    return Embedder(settings.embedding_model)


@lru_cache
def get_vectorstore() -> VectorStore:
    return VectorStore(settings.data_dir, settings.chroma_collection)


@lru_cache
def get_llm() -> LLMClient:
    return LLMClient(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        refusal=settings.refusal_message,
    )
