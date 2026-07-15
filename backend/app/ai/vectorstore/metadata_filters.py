import uuid
from dataclasses import dataclass, field


@dataclass
class MetadataFilter:
    """Structured filter criteria for scoping vector search results.

    All fields are optional — an empty filter matches everything within
    the organization's collection (organization scoping is already
    enforced by using a per-org collection, not by this filter).
    """

    document_ids: list[uuid.UUID] = field(default_factory=list)
    file_types: list[str] = field(default_factory=list)
    exclude_document_ids: list[uuid.UUID] = field(default_factory=list)

    def to_chroma_where(self) -> dict | None:
        """Convert this filter into ChromaDB's `where` clause format."""
        conditions: list[dict] = []

        if self.document_ids:
            conditions.append(
                {"document_id": {"$in": [str(doc_id) for doc_id in self.document_ids]}}
            )

        if self.file_types:
            conditions.append({"file_type": {"$in": self.file_types}})

        if self.exclude_document_ids:
            conditions.append(
                {"document_id": {"$nin": [str(doc_id) for doc_id in self.exclude_document_ids]}}
            )

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]

        return {"$and": conditions}