"""Benchmarks ChromaDB vs FAISS for embedding + search performance.

Run from the backend/ directory: python ../scripts/benchmark_vectorstore.py
"""
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.ai.embeddings import get_embedder
from app.ai.vectorstore.chroma_client import get_or_create_collection
from app.ai.vectorstore.faiss_client import get_faiss_store

SAMPLE_TEXTS = [
    f"This is sample document number {i} discussing quarterly revenue, employee policies, "
    f"and various company operations for benchmarking purposes."
    for i in range(200)
]


def benchmark_chroma(embeddings: list[list[float]]) -> float:
    collection = get_or_create_collection(f"benchmark_{uuid.uuid4().hex[:8]}")
    ids = [str(uuid.uuid4()) for _ in embeddings]
    metadatas = [{"index": i} for i in range(len(embeddings))]

    start = time.perf_counter()
    collection.add(ids=ids, embeddings=embeddings, documents=SAMPLE_TEXTS, metadatas=metadatas)
    collection.query(query_embeddings=[embeddings[0]], n_results=5)
    elapsed = time.perf_counter() - start
    return elapsed


def benchmark_faiss(embeddings: list[list[float]]) -> float:
    store = get_faiss_store(organization_id=f"benchmark_{uuid.uuid4().hex[:8]}")
    metadatas = [{"index": i} for i in range(len(embeddings))]

    start = time.perf_counter()
    store.add(embeddings, metadatas)
    store.search(embeddings[0], top_k=5)
    elapsed = time.perf_counter() - start
    return elapsed


if __name__ == "__main__":
    print(f"Generating embeddings for {len(SAMPLE_TEXTS)} sample documents...")
    embedder = get_embedder()
    embeddings = embedder.embed_batch(SAMPLE_TEXTS)

    print("\nBenchmarking ChromaDB (add + query)...")
    chroma_time = benchmark_chroma(embeddings)
    print(f"ChromaDB: {chroma_time:.3f}s")

    print("\nBenchmarking FAISS (add + query)...")
    faiss_time = benchmark_faiss(embeddings)
    print(f"FAISS: {faiss_time:.3f}s")

    print(f"\nFAISS was {chroma_time / faiss_time:.1f}x faster for this workload"
          if faiss_time < chroma_time else
          f"\nChromaDB was {faiss_time / chroma_time:.1f}x faster for this workload")