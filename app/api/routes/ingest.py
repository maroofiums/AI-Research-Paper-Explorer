"""
POST /ingest/arxiv

Ingests one or more papers from arXiv: fetches metadata, downloads and
parses the PDF, chunks the full text, and persists everything as JSON under
data/papers/. This local JSON store is a Phase 1 placeholder -- Phase 2
replaces it with FAISS indices for both paper-level and chunk-level
embeddings, but the ingestion logic here stays the same either way.
"""

import asyncio
import json

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models.schemas import IngestedPaper, IngestRequest, IngestResponse, Paper
from app.services import arxiv_loader, pdf_parser
from app.services.chunker import chunk_text

router = APIRouter(prefix="/ingest", tags=["ingest"])


def _save_paper(paper: Paper, chunks: list) -> None:
    """Persist a paper's metadata and chunks as a single JSON file."""

    out_path = settings.data_dir / "papers" / f"{paper.arxiv_id}.json"
    payload = {
        "paper": paper.model_dump(mode="json"),
        "chunks": [chunk.model_dump() for chunk in chunks],
    }
    out_path.write_text(json.dumps(payload, indent=2))


async def _ingest_one(paper: Paper) -> IngestedPaper:
    full_text = await pdf_parser.fetch_and_extract_text(paper.pdf_url)
    chunks = chunk_text(
        text=full_text,
        paper_id=paper.arxiv_id,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )
    _save_paper(paper, chunks)
    return IngestedPaper(paper=paper, num_chunks=len(chunks))


@router.post("/arxiv", response_model=IngestResponse)
async def ingest_arxiv(request: IngestRequest) -> IngestResponse:
    if not request.arxiv_id and not request.query:
        raise HTTPException(
            status_code=400, detail="Provide either 'arxiv_id' or 'query'"
        )
    if request.arxiv_id and request.query:
        raise HTTPException(
            status_code=400,
            detail="Provide only one of 'arxiv_id' or 'query', not both",
        )

    try:
        if request.arxiv_id:
            paper = await asyncio.to_thread(arxiv_loader.fetch_by_id, request.arxiv_id)
            papers = [paper]
        else:
            papers = await asyncio.to_thread(
                arxiv_loader.search, request.query, request.max_results
            )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    ingested = [await _ingest_one(paper) for paper in papers]
    return IngestResponse(ingested=ingested)