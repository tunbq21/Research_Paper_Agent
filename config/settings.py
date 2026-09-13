"""
Application settings using Pydantic BaseSettings.
Automatically loads values from environment variables and .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized configuration for the Research Paper Agent."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Google AI ---
    google_api_key: str

    # --- LLM Settings ---
    gemini_llm_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "models/text-embedding-004"

    # --- ChromaDB Settings ---
    chroma_persist_directory: str = "./data/chroma_db"
    chroma_collection_name: str = "research_papers"

    # --- Chunking Settings ---
    chunk_size: int = 500
    chunk_overlap: int = 50

    # --- Retrieval Settings ---
    retrieval_top_k: int = 5

    # --- App Settings ---
    app_log_level: str = "INFO"


# Singleton instance — import này ở mọi module khác
settings = Settings()
