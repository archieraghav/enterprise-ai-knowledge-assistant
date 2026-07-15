import uuid
from typing import TypedDict

from app.ai.citation_formatter import Citation
from app.ai.retriever import RetrievedChunk


class RAGState(TypedDict):
    """Shared state passed between nodes in the RAG graph.

    Each node reads what it needs from this dict and writes back updates —
    LangGraph merges the returned partial dicts into the running state.
    """

    organization_id: uuid.UUID
    question: str
    retrieved_chunks: list[RetrievedChunk]
    answer: str
    citations: list[Citation]