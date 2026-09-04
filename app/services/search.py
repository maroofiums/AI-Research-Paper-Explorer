import json
from dataclasses import dataclass
from typing import List

from app.config import settings
from app.models.schemas import Chunk, Paper
from app.services.vector_store import get_paper_store, get_chunk_store


@dataclass
class PaperResult:
    paper: Paper
    score: float


@dataclass
class ChunkResult:
    chunk: Chunk
    score: float


def _load_paper(arxiv_id: str) -> Paper:

    path = settings.data_dir / "papers" / f"{arxiv_id}.json"
    payload = json.load(path.read_text())
    return Paper(**payload["paper"])

def _load_chunk(paper_id: str, chunk_id: str) -> Chunk:

    path = settings.data_dir / "papers" / f"{paper_id}.json"
    payload = json.load(path.read_text())
    chunk_data = next(c for c in payload["chunks"] if c["chunk_id"] == chunk_id)
    return Chunk(**chunk_data)

def search_papers(query: str, k: int = 5) -> List[PaperResult]:

    store = get_paper_store()
    results = store.similarity_search_with_score(query=query, k=k)

    return [
        PaperResult(
            paper=_load_paper(doc.metadata["arxiv_id"]),
            score=score
        )
        for doc, score in results
    ]


def search_chunks(query: str, k: int = 5, paper_id: str | None = None) -> List[ChunkResult]:

    store = get_chunk_store()
    filter_dict = {"paper_id": paper_id} if paper_id else None
    results = store.similarity_search_with_score(
        query=query,
        k=k,
        filter=filter_dict
    )

    return [
        ChunkResult(
            chunk=_load_chunk(doc.metadata["paper_id"], doc.metadata["chunk_id"]),
            score=score
        )
        for doc, score in results
    ]
