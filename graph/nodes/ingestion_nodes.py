"""
Ingestion Agent Nodes: Handles the full PDF processing pipeline.
Nodes: pdf_parser → text_chunker → embedder_indexer
"""
from pathlib import Path

from langchain_core.messages import AIMessage
from loguru import logger

from core.embeddings import get_embeddings
from schemas.agent_state import AgentState
from services.chunking_service import split_text_into_chunks
from services.pdf_service import extract_text_from_pdf
from services.vector_store_service import add_documents_to_store, get_vector_store


def pdf_parser_node(state: AgentState) -> dict:
    """Extracts raw text from the uploaded PDF file."""
    logger.info("--- INGESTION AGENT: [1/3] Parsing PDF ---")
    pdf_path = state.get("pdf_path")
    if not pdf_path:
        logger.error("No pdf_path found in state.")
        return {}

    text = extract_text_from_pdf(pdf_path)
    # Store extracted text temporarily in messages for the next node to pick up
    return {
        "messages": [AIMessage(content=f"[INTERNAL] PDF parsed. Length: {len(text)} chars.")],
        "_raw_text": text,  # passed implicitly via state update
    }


def text_chunker_node(state: AgentState) -> dict:
    """Splits the extracted PDF text into overlapping chunks."""
    logger.info("--- INGESTION AGENT: [2/3] Chunking Text ---")
    # Retrieve raw text from the last internal message
    raw_text = state.get("_raw_text", "")
    if not raw_text:
        # Fallback: re-extract if state doesn't carry raw text
        raw_text = extract_text_from_pdf(state["pdf_path"])

    source_name = Path(state["pdf_path"]).stem
    chunks = split_text_into_chunks(raw_text, source_name=source_name)

    return {
        "messages": [AIMessage(content=f"[INTERNAL] Chunking done. {len(chunks)} chunks created.")],
        "_chunks": chunks,
    }


def embedder_indexer_node(state: AgentState) -> dict:
    """Embeds chunks and stores them in ChromaDB."""
    logger.info("--- INGESTION AGENT: [3/3] Embedding & Indexing ---")
    chunks = state.get("_chunks", [])
    if not chunks:
        logger.error("No chunks to index.")
        return {"is_ingested": False}

    pdf_stem = Path(state["pdf_path"]).stem
    # Sanitize collection name: ChromaDB requires alphanumeric + hyphens
    collection_name = "".join(c if c.isalnum() else "-" for c in pdf_stem).lower()[:63]

    embeddings = get_embeddings()
    vector_store = get_vector_store(embeddings, collection_name=collection_name)
    add_documents_to_store(vector_store, chunks)

    logger.success(f"Ingestion complete. Collection: '{collection_name}'")
    return {
        "is_ingested": True,
        "collection_name": collection_name,
        "messages": [AIMessage(content=f"✅ Paper indexed successfully into collection '{collection_name}'.")],
    }
