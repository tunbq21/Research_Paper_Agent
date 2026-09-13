"""
Retrieval Agent Nodes: Handles intelligent search in the vector database.
Nodes: query_rewriter → vector_search
"""
from langchain_core.messages import AIMessage, HumanMessage
from loguru import logger

from core.embeddings import get_embeddings
from core.llm import get_llm
from prompts.query_rewriter_prompt import query_rewriter_prompt
from schemas.agent_state import AgentState
from services.vector_store_service import get_vector_store, similarity_search


def _format_chat_history(messages: list) -> str:
    """Formats the message list into a readable string for prompts."""
    history_lines = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            history_lines.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage) and not msg.content.startswith("[INTERNAL]"):
            history_lines.append(f"Assistant: {msg.content}")
    return "\n".join(history_lines[-6:])  # last 3 exchanges


def query_rewriter_node(state: AgentState) -> dict:
    """
    Rewrites the user's question for better vector search performance.
    Incorporates chat history to handle follow-up questions correctly.
    """
    logger.info("--- RETRIEVAL AGENT: [1/2] Rewriting Query ---")
    question = state.get("question", "")
    chat_history = _format_chat_history(state.get("messages", []))

    llm = get_llm()
    chain = query_rewriter_prompt | llm
    response = chain.invoke({"question": question, "chat_history": chat_history})

    rewritten = response.content.strip()
    logger.info(f"Original:  {question}")
    logger.info(f"Rewritten: {rewritten}")

    return {"rewritten_query": rewritten}


def vector_search_node(state: AgentState) -> dict:
    """
    Searches ChromaDB for the top-k chunks most relevant to the query.
    """
    logger.info("--- RETRIEVAL AGENT: [2/2] Vector Search ---")
    query = state.get("rewritten_query") or state.get("question", "")
    collection_name = state.get("collection_name")

    if not collection_name:
        logger.error("No collection_name in state. Was the PDF ingested?")
        return {"retrieved_chunks": []}

    embeddings = get_embeddings()
    vector_store = get_vector_store(embeddings, collection_name=collection_name)
    docs = similarity_search(vector_store, query)

    # Format chunks with index labels for citation referencing
    formatted_chunks = [
        f"[Chunk {i + 1}] (source: {doc.metadata.get('source', 'unknown')}, "
        f"chunk_index: {doc.metadata.get('chunk_index', '?')})\n{doc.page_content}"
        for i, doc in enumerate(docs)
    ]

    logger.info(f"Retrieved {len(formatted_chunks)} chunks.")
    return {"retrieved_chunks": formatted_chunks}
