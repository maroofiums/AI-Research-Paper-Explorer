"""
Pydantic schemas shared across the app: arXiv paper metadata, text chunks,
and the request/response contracts for the ingest API.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class Paper(BaseModel):
    """Metadata for a single arXiv paper, as returned by the arXiv API."""

    arxiv_id: str = Field(..., description="arXiv identifier, e.g. '2401.12345'")
    title: str
    abstract: str
    authors: list[str]
    published: datetime
    updated: datetime
    categories: list[str]
    pdf_url: str


class Chunk(BaseModel):
    """A single chunk of a paper's full text, ready for embedding in Phase 2."""

    chunk_id: str = Field(..., description="Format: '{arxiv_id}_{chunk_index}'")
    paper_id: str = Field(..., description="arXiv ID this chunk belongs to")
    chunk_index: int
    text: str
    word_count: int


class IngestRequest(BaseModel):
    """Request body for POST /ingest/arxiv. Provide exactly one of the two."""

    arxiv_id: str | None = Field(
        default=None, description="Ingest a specific paper, e.g. '2401.12345'"
    )
    query: str | None = Field(
        default=None, description="Search arXiv and ingest the top matches"
    )
    max_results: int = Field(
        default=1, ge=1, le=10, description="Only used when 'query' is set"
    )


class IngestedPaper(BaseModel):
    """Summary of one successfully ingested paper, returned in IngestResponse."""

    paper: Paper
    num_chunks: int


class IngestResponse(BaseModel):
    ingested: list[IngestedPaper]
