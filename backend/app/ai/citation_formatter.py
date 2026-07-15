from dataclasses import dataclass

from app.ai.retriever import RetrievedChunk


@dataclass
class Citation:
    """A single source citation, ready to display alongside an AI-generated answer."""

    document_id: str
    document_title: str
    excerpt: str


def format_citations(chunks: list[RetrievedChunk], max_excerpt_length: int = 200) -> list[Citation]:
    """Convert retrieved chunks into deduplicated, display-ready citations.

    Deduplicates by document_id — if multiple chunks from the same document
    were retrieved, only the most relevant (first) one is shown as a citation,
    since showing 3 citations to the same document is noisy for the user.
    """
    seen_document_ids: set[str] = set()
    citations: list[Citation] = []

    for chunk in chunks:
        if chunk.document_id in seen_document_ids:
            continue
        seen_document_ids.add(chunk.document_id)

        excerpt = chunk.content[:max_excerpt_length]
        if len(chunk.content) > max_excerpt_length:
            excerpt += "..."

        citations.append(
            Citation(
                document_id=chunk.document_id,
                document_title=chunk.document_title,
                excerpt=excerpt,
            )
        )

    return citations