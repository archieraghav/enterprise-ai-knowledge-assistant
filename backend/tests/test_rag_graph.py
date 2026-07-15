import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.ai.graphs.rag_graph import build_rag_graph
from app.ai.retriever import RetrievedChunk


def _make_fake_chunks() -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            content="Our company offers 20 days of paid vacation per year.",
            document_id="doc-1",
            document_title="policy.txt",
            chunk_index=0,
            distance=0.35,
        )
    ]


@pytest.mark.asyncio
async def test_rag_graph_returns_answer_and_citations() -> None:
    fake_chunks = _make_fake_chunks()

    with patch("app.ai.graphs.rag_graph.retrieve_relevant_chunks", return_value=fake_chunks):
        with patch("app.ai.graphs.rag_graph.get_llm") as mock_get_llm:
            mock_llm = AsyncMock()
            mock_llm.generate.return_value = "Employees get 20 days of paid vacation per year."
            mock_get_llm.return_value = mock_llm

            graph = build_rag_graph()
            result = await graph.ainvoke(
                {
                    "organization_id": uuid.uuid4(),
                    "question": "How many vacation days do employees get?",
                }
            )

    assert result["answer"] == "Employees get 20 days of paid vacation per year."
    assert len(result["citations"]) == 1
    assert result["citations"][0].document_title == "policy.txt"


@pytest.mark.asyncio
async def test_rag_graph_handles_no_retrieved_chunks() -> None:
    with patch("app.ai.graphs.rag_graph.retrieve_relevant_chunks", return_value=[]):
        graph = build_rag_graph()
        result = await graph.ainvoke(
            {
                "organization_id": uuid.uuid4(),
                "question": "What is the meaning of life?",
            }
        )

    assert "couldn't find any relevant information" in result["answer"]
    assert result["citations"] == []


@pytest.mark.asyncio
async def test_rag_graph_deduplicates_citations_from_same_document() -> None:
    fake_chunks = [
        RetrievedChunk(
            content="First chunk from the same document.",
            document_id="doc-1",
            document_title="policy.txt",
            chunk_index=0,
            distance=0.2,
        ),
        RetrievedChunk(
            content="Second chunk from the same document.",
            document_id="doc-1",
            document_title="policy.txt",
            chunk_index=1,
            distance=0.4,
        ),
    ]

    with patch("app.ai.graphs.rag_graph.retrieve_relevant_chunks", return_value=fake_chunks):
        with patch("app.ai.graphs.rag_graph.get_llm") as mock_get_llm:
            mock_llm = AsyncMock()
            mock_llm.generate.return_value = "Some answer based on the policy."
            mock_get_llm.return_value = mock_llm

            graph = build_rag_graph()
            result = await graph.ainvoke(
                {
                    "organization_id": uuid.uuid4(),
                    "question": "Tell me about the policy.",
                }
            )

    # Both chunks came from doc-1, so citations should be deduplicated to one entry.
    assert len(result["citations"]) == 1


@pytest.mark.asyncio
async def test_rag_graph_calls_llm_with_system_prompt() -> None:
    fake_chunks = _make_fake_chunks()

    with patch("app.ai.graphs.rag_graph.retrieve_relevant_chunks", return_value=fake_chunks):
        with patch("app.ai.graphs.rag_graph.get_llm") as mock_get_llm:
            mock_llm = AsyncMock()
            mock_llm.generate.return_value = "An answer."
            mock_get_llm.return_value = mock_llm

            graph = build_rag_graph()
            await graph.ainvoke(
                {
                    "organization_id": uuid.uuid4(),
                    "question": "A question.",
                }
            )

    mock_llm.generate.assert_called_once()
    call_kwargs = mock_llm.generate.call_args.kwargs
    assert "system_prompt" in call_kwargs
    assert "ONLY the provided document excerpts" in call_kwargs["system_prompt"]