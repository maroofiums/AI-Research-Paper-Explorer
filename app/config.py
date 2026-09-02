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

    data_dir: Path = Path("./data")

    chunk_size: int = 1000
    chunk_overlap: int = 100

    paper_embedding_model: str = "allenai/specter2_base"
    chunk_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    paper_index_dir: Path = Path("./data/faiss_paper_index")
    chunk_index_dir: Path = Path("./data/faiss_chunk_index")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

(settings.data_dir / "papers").mkdir(parents=True, exist_ok=True)

settings.paper_index_dir.mkdir(parents=True, exist_ok=True)
settings.chunk_index_dir.mkdir(parents=True, exist_ok=True)