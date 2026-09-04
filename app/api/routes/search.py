"""
GET /search/papers, GET /search/chunks

Exposes the semantic search functions in services/search.py over HTTP.
Query parameters carry validation bounds the same way IngestRequest does,
so bad input (k=0, k=1000) is rejected at the FastAPI layer before it ever
reaches FAISS.
"""

import asyncio

from fastapi import APIRouter, Query

from app.models.schemas import (
    ChunkSearchResponse,
    ChunkSearchResult,
    PaperSearchResponse,
    PaperSearchResult,
)
from app.services import search

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/papers", response_model=PaperSearchResponse)
async def search_papers(
    query: str = Query(..., min_length=1, description="Free-text search query"),
    k: int = Query(default=5, ge=1, le=50, description="Number of results to return"),
) -> PaperSearchResponse:
    results = await asyncio.to_thread(search.search_papers, query, k)
    return PaperSearchResponse(
        results=[PaperSearchResult(paper=r.paper, score=r.score) for r in results]
    )


@router.get("/chunks", response_model=ChunkSearchResponse)
async def search_chunks(
    query: str = Query(..., min_length=1, description="Free-text search query"),
    k: int = Query(default=5, ge=1, le=50, description="Number of results to return"),
    paper_id: str | None = Query(
        default=None, description="Restrict results to one paper's chunks"
    ),
) -> ChunkSearchResponse:
    results = await asyncio.to_thread(search.search_chunks, query, k, paper_id)
    return ChunkSearchResponse(
        results=[ChunkSearchResult(chunk=r.chunk, score=r.score) for r in results]
    )