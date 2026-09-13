"""
Embeddings Factory: Creates and returns a configured LangChain Embeddings instance.
Centralizes all embedding model initialization.
"""
from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from loguru import logger

from config.settings import settings


@lru_cache(maxsize=1)
def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """
    Returns a cached instance of the Google Gemini embedding model.

    Uses Google's `text-embedding-004` model by default, which provides
    strong multilingual semantic understanding suitable for academic text.

    Returns:
        A configured GoogleGenerativeAIEmbeddings instance.
    """
    logger.info(f"Initializing Embedding model: {settings.gemini_embedding_model}")
    return GoogleGenerativeAIEmbeddings(
        model=settings.gemini_embedding_model,
        google_api_key=settings.google_api_key,
    )
