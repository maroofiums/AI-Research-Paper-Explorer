"""
Wraps LangChain's FAISS vector store for our two indices (paper-level and
chunk-level): handles creation, loading from disk, and adding new items.

Search itself lives in a separate module -- this file only owns the index
lifecycle (create/load/persist), so search logic can stay simple.
"""

from functools import lru_cache
from pathlib import Path
from typing import List

import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings
from app.models.schemas import Chunk, Paper
from app.services.embedder import (
    chunk_to_text,
    get_chunk_embeddings,
    get_paper_embeddings,
    paper_to_text,
)


def _load_or_create(index_dir: Path, embeddings: HuggingFaceEmbeddings) -> FAISS:
    """
    Load a persisted FAISS index from disk if one exists, otherwise build a
    genuinely empty index -- correctly dimensioned for this embedding model
    -- ready to accept the first `add_documents` call.
    """

    index_file = index_dir / "index.faiss"
    if index_file.exists():
        return FAISS.load_local(
            str(index_dir), embeddings, allow_dangerous_deserialization=True
        )

    embedding_dim = len(embeddings.embed_query("dimension probe"))
    return FAISS(
        embedding_function=embeddings,
        index=faiss.IndexFlatL2(embedding_dim),
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )


@lru_cache(maxsize=1)
def get_paper_store() -> FAISS:
    return _load_or_create(settings.paper_index_dir, get_paper_embeddings())


@lru_cache(maxsize=1)
def get_chunk_store() -> FAISS:
    return _load_or_create(settings.chunk_index_dir, get_chunk_embeddings())


def add_paper(paper: Paper) -> None:
    """Embed a paper (title + abstract) and add it to the paper-level index."""

    store = get_paper_store()
    doc = Document(
        page_content=paper_to_text(paper), metadata={"arxiv_id": paper.arxiv_id}
    )
    store.add_documents([doc], ids=[paper.arxiv_id])
    store.save_local(str(settings.paper_index_dir))


def add_chunks(chunks: List[Chunk]) -> None:
    """Embed a paper's chunks and add them to the chunk-level index."""

    if not chunks:
        return

    store = get_chunk_store()
    docs = [
        Document(
            page_content=chunk_to_text(chunk),
            metadata={"chunk_id": chunk.chunk_id, "paper_id": chunk.paper_id},
        )
        for chunk in chunks
    ]
    store.add_documents(docs, ids=[chunk.chunk_id for chunk in chunks])
    store.save_local(str(settings.chunk_index_dir))