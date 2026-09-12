"""
Vector Store Service: Manages interactions with ChromaDB.
Provides a clean abstraction over LangChain's Chroma integration
for adding documents and performing similarity searches.
"""
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from loguru import logger

from config.settings import settings


def get_vector_store(
    embedding_function: Embeddings,
    collection_name: str | None = None,
) -> Chroma:
    """
    Returns a Chroma vector store instance for a given collection.

    If the collection already exists at the persist directory, it is
    loaded. Otherwise, a new empty collection is created.

    Args:
        embedding_function: The embedding model used to encode text.
        collection_name: The Chroma collection name. Defaults to settings.

    Returns:
        A ready-to-use Chroma vector store instance.
    """
    collection = collection_name or settings.chroma_collection_name
    logger.info(
        f"Connecting to Chroma collection: '{collection}' "
        f"at '{settings.chroma_persist_directory}'"
    )
    return Chroma(
        collection_name=collection,
        embedding_function=embedding_function,
        persist_directory=settings.chroma_persist_directory,
    )


def add_documents_to_store(
    vector_store: Chroma,
    documents: list[Document],
) -> None:
    """
    Embeds and adds a list of Document chunks to the vector store.

    Args:
        vector_store: The Chroma vector store to write to.
        documents: List of Document objects to embed and store.
    """
    logger.info(f"Indexing {len(documents)} document chunks into vector store...")
    vector_store.add_documents(documents)
    logger.info("Indexing complete.")


def similarity_search(
    vector_store: Chroma,
    query: str,
    top_k: int | None = None,
) -> list[Document]:
    """
    Retrieves the most semantically similar chunks for a given query.

    Args:
        vector_store: The Chroma vector store to search in.
        query: The natural language query string.
        top_k: Number of results to retrieve. Defaults to settings.

    Returns:
        A list of the top-k most relevant Document chunks.
    """
    k = top_k or settings.retrieval_top_k
    logger.info(f"Performing similarity search (top_k={k}) for query: '{query[:80]}...'")
    results = vector_store.similarity_search(query, k=k)
    logger.info(f"Retrieved {len(results)} chunks.")
    return results


def delete_collection(collection_name: str, embedding_function: Embeddings) -> None:
    """
    Deletes a Chroma collection. Useful for cleanup or re-ingestion.

    Args:
        collection_name: Name of the collection to delete.
        embedding_function: Required to connect to the store first.
    """
    logger.warning(f"Deleting Chroma collection: '{collection_name}'")
    store = get_vector_store(embedding_function, collection_name)
    store.delete_collection()
    logger.info(f"Collection '{collection_name}' deleted.")
