from langgraph.graph import END, StateGraph

from app.ai.citation_formatter import format_citations
from app.ai.graphs.state import RAGState
from app.ai.llm import get_llm
from app.ai.prompts.qa_prompt import SYSTEM_PROMPT, build_qa_prompt
from app.ai.retriever import retrieve_relevant_chunks
from app.core.logging import get_logger

logger = get_logger(__name__)


async def retrieve_node(state: RAGState) -> dict:
    """Retrieve relevant document chunks for the user's question."""
    chunks = retrieve_relevant_chunks(
        organization_id=state["organization_id"],
        query=state["question"],
        top_k=5,
    )
    logger.info("Retrieved %d chunks for question: %s", len(chunks), state["question"])
    return {"retrieved_chunks": chunks}


async def generate_node(state: RAGState) -> dict:
    """Generate an answer using the LLM, grounded in retrieved context."""
    chunks = state["retrieved_chunks"]

    if not chunks:
        return {"answer": "I couldn't find any relevant information in the uploaded documents to answer this question."}

    from app.ai.language_service import build_language_instruction

    prompt = build_qa_prompt(state["question"], chunks)
    language_instruction = build_language_instruction(state["question"])
    system_prompt = SYSTEM_PROMPT + language_instruction

    llm = get_llm()
    answer = await llm.generate(prompt, system_prompt=system_prompt)
    return {"answer": answer}

async def cite_node(state: RAGState) -> dict:
    """Format retrieved chunks into clean, deduplicated citations."""
    citations = format_citations(state["retrieved_chunks"])
    return {"citations": citations}


def build_rag_graph():
    """Construct and compile the RAG state graph: retrieve -> generate -> cite."""
    graph = StateGraph(RAGState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_node("cite", cite_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "cite")
    graph.add_edge("cite", END)

    return graph.compile()


_compiled_graph = None


def get_rag_graph():
    """Return a singleton compiled RAG graph instance."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_rag_graph()
    return _compiled_graph