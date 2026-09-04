from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings
from app.models.schemas import Chunk, Paper

@lru_cache(maxsize=1)
def get_paper_embeddings() -> HuggingFaceEmbeddings:

    return HuggingFaceEmbeddings(model_name=settings.paper_embedding_model)

@lru_cache(maxsize=1)
def get_chunk_embeddings() -> HuggingFaceEmbeddings:

    return HuggingFaceEmbeddings(model_name=settings.chunk_embedding_model)

def paper_to_text(paper: Paper) -> str:

    return f"{paper.title}\n\n{paper.abstract}"

def chunk_to_text(chunk: Chunk) -> str:

    return chunk.text