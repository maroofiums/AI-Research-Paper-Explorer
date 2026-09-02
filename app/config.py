"""
Centralized application configuration.

Loads settings from environment variables (and a local .env file, if present)
using pydantic-settings. Every other module should import `settings` from
here rather than reading os.environ directly — this keeps configuration
in one auditable place and gives us validation for free.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # arXiv API
    arxiv_api_base_url: str = "http://export.arxiv.org/api/query"

    # Local storage
    data_dir: Path = Path("./data")

    # Chunking (measured in words, not tokens — see app/services/chunker.py)
    chunk_size_words: int = 400
    chunk_overlap_words: int = 50

    # Phase 2 — embedding models (referenced now, used starting Phase 2)
    paper_embedding_model: str = "allenai/specter2_base"
    chunk_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

# Ensure the data directory (and the subfolder we use in Phase 1) exists at import time,
# so routes don't need to check for it on every request.
(settings.data_dir / "papers").mkdir(parents=True, exist_ok=True)
