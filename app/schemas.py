from typing import Optional

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    path: str = Field(..., description="Absolute or relative path to a local PDF file")


class IngestResponse(BaseModel):
    source: str
    pages: int
    chunks_added: int


class Citation(BaseModel):
    source: str
    page: int
    snippet: str


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = None


class QueryResponse(BaseModel):
    answer: str
    grounded: bool
    citations: list[Citation]
