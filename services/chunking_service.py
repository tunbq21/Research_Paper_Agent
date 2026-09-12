"""
Chunking Service: Splits extracted text into overlapping chunks
using LangChain's RecursiveCharacterTextSplitter.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from loguru import logger

from config.settings import settings


def split_text_into_chunks(
    text: str,
    source_name: str = "unknown",
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Document]:
    """
    Splits a large text string into overlapping Document chunks.

    Uses RecursiveCharacterTextSplitter, which intelligently splits
    on paragraph breaks, newlines, and spaces — prioritizing semantic
    boundaries over hard character counts.

    Args:
        text: The full text to split.
        source_name: A label (e.g., filename) to attach as metadata.
        chunk_size: Token/character size per chunk. Defaults to settings.
        chunk_overlap: Overlap between consecutive chunks. Defaults to settings.

    Returns:
        A list of LangChain Document objects, each with page_content
        and metadata (source, chunk_index).
    """
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    raw_chunks: list[str] = splitter.split_text(text)

    documents = [
        Document(
            page_content=chunk,
            metadata={"source": source_name, "chunk_index": i},
        )
        for i, chunk in enumerate(raw_chunks)
    ]

    logger.info(
        f"Chunking complete. Source: '{source_name}', "
        f"Chunks: {len(documents)}, "
        f"chunk_size={chunk_size}, overlap={chunk_overlap}"
    )
    return documents
