"""
Semantic search over ingested papers and chunks.

Two distinct retrieval tasks, kept as separate functions since they query
different FAISS indices with different embedding models (see embedder.py
and vector_store.py for why they're split):

- search_papers: "find papers like X" -- paper-to-paper similarity
- search_chunks: "find passages relevant to this question" -- RAG retrieval
"""

import json
from dataclasses import dataclass

from app.config import settings
from app.models.schemas import Chunk, Paper
from app.services.vector_store import get_chunk_store, get_paper_store


@dataclass
class PaperResult:
    paper: Paper
    score: float  # L2 distance -- lower is more similar


@dataclass
class ChunkResult:
    chunk: Chunk
    score: float  # L2 distance -- lower is more similar


def _load_paper(arxiv_id: str) -> Paper:
    """
    Hydrate a full Paper from its saved JSON. FAISS's docstore only holds
    the title+abstract text and arxiv_id we embedded -- the rest of the
    metadata (authors, categories, pdf_url, ...) lives in the JSON file
    ingest.py wrote. FAISS is the index; the JSON files are the source of
    truth for content.
    """

    path = settings.data_dir / "papers" / f"{arxiv_id}.json"
    payload = json.loads(path.read_text())
    return Paper(**payload["paper"])


def _load_chunk(paper_id: str, chunk_id: str) -> Chunk:
    """Hydrate a full Chunk the same way, from its parent paper's JSON."""

    path = settings.data_dir / "papers" / f"{paper_id}.json"
    payload = json.loads(path.read_text())
    chunk_data = next(c for c in payload["chunks"] if c["chunk_id"] == chunk_id)
    return Chunk(**chunk_data)


def search_papers(query: str, k: int = 5) -> list[PaperResult]:
    """Find papers most similar to a free-text query."""

    store = get_paper_store()
    results = store.similarity_search_with_score(query, k=k)
    return [
        PaperResult(paper=_load_paper(doc.metadata["arxiv_id"]), score=score)
        for doc, score in results
    ]


def search_chunks(
    query: str, k: int = 5, paper_id: str | None = None
) -> list[ChunkResult]:
    """
    Find chunks most relevant to a question -- the retrieval step of RAG.

    `paper_id` scopes the search to one paper's chunks only (for "chat with
    this paper"). Left as None, it searches across every ingested paper's
    chunks at once (for open-ended research questions).
    """

    store = get_chunk_store()
    filter_dict = {"paper_id": paper_id} if paper_id else None
    results = store.similarity_search_with_score(query, k=k, filter=filter_dict)
    return [
        ChunkResult(
            chunk=_load_chunk(doc.metadata["paper_id"], doc.metadata["chunk_id"]),
            score=score,
        )
        for doc, score in results
    ]