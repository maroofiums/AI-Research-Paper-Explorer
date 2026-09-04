"""
Wraps our two embedding models (paper-level and chunk-level) as LangChain
Embeddings objects, so both plug directly into LangChain's FAISS vector
store without any custom glue code.
"""

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings
from app.models.schemas import Chunk, Paper


@lru_cache(maxsize=1)
def get_paper_embeddings() -> HuggingFaceEmbeddings:
    """Embedding model for paper-to-paper similarity (title + abstract)."""

    return HuggingFaceEmbeddings(model_name=settings.paper_embedding_model)


@lru_cache(maxsize=1)
def get_chunk_embeddings() -> HuggingFaceEmbeddings:
    """Embedding model for question-to-chunk retrieval (RAG)."""

    return HuggingFaceEmbeddings(model_name=settings.chunk_embedding_model)


def paper_to_text(paper: Paper) -> str:
    """
    Canonical text representation of a paper for embedding: title + abstract,
    not the full paper body. This mirrors the title/abstract pairs SPECTER-
    family models are trained on, so the input shape matches what the model
    actually learned from.
    """

    return f"{paper.title}\n\n{paper.abstract}"


def chunk_to_text(chunk: Chunk) -> str:
    """Canonical text representation of a chunk for embedding."""

    return chunk.text