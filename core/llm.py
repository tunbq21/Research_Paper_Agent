"""
LLM Factory: Creates and returns a configured LangChain LLM instance.
Centralizes all LLM initialization so swapping providers only requires
changes in this one file.
"""
from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI
from loguru import logger

from config.settings import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatGoogleGenerativeAI:
    """
    Returns a cached instance of the Google Gemini chat model.

    The @lru_cache decorator ensures only one instance is created
    for the lifetime of the application, avoiding repeated API client
    initialization overhead.

    Returns:
        A configured ChatGoogleGenerativeAI instance.
    """
    logger.info(f"Initializing LLM: {settings.gemini_llm_model}")
    return ChatGoogleGenerativeAI(
        model=settings.gemini_llm_model,
        google_api_key=settings.google_api_key,
        temperature=0.2,  # Low temperature for factual, grounded answers
        convert_system_message_to_human=True,
    )
