import pickle
import uuid
from pathlib import Path

import faiss
import numpy as np

FAISS_STORAGE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "faiss_indexes"
FAISS_STORAGE_DIR.mkdir(exist_ok=True)


class FaissVectorStore:
    """A simple flat-index FAISS vector store, scoped to one organization.

    This is an optional local alternative to ChromaDB — useful for
    benchmarking or for environments where running a separate ChromaDB
    server isn't desirable. Each organization gets its own index file
    persisted to disk.
    """

    def __init__(self, organization_id: str, dimension: int = 384) -> None:
        self.organization_id = organization_id
        self.dimension = dimension
        self._index_path = FAISS_STORAGE_DIR / f"{organization_id}.index"
        self._metadata_path = FAISS_STORAGE_DIR / f"{organization_id}_meta.pkl"

        if self._index_path.exists():
            self._index = faiss.read_index(str(self._index_path))
            with open(self._metadata_path, "rb") as f:
                self._metadata_store: list[dict] = pickle.load(f)
        else:
            self._index = faiss.IndexFlatL2(dimension)
            self._metadata_store = []

    def add(self, embeddings: list[list[float]], metadatas: list[dict]) -> None:
        """Add vectors and their associated metadata to the index."""
        vectors = np.array(embeddings, dtype="float32")
        self._index.add(vectors)
        self._metadata_store.extend(metadatas)
        self._persist()

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        """Return the top_k nearest neighbors with their metadata and distance."""
        if self._index.ntotal == 0:
            return []

        query_vector = np.array([query_embedding], dtype="float32")
        distances, indices = self._index.search(query_vector, min(top_k, self._index.ntotal))

        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            results.append({"metadata": self._metadata_store[idx], "distance": float(distance)})
        return results

    def count(self) -> int:
        return self._index.ntotal

    def _persist(self) -> None:
        faiss.write_index(self._index, str(self._index_path))
        with open(self._metadata_path, "wb") as f:
            pickle.dump(self._metadata_store, f)


def get_faiss_store(organization_id: str, dimension: int = 384) -> FaissVectorStore:
    """Factory function returning a FAISS store scoped to one organization."""
    return FaissVectorStore(organization_id=organization_id, dimension=dimension)