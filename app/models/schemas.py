"""
Pydantic schemas shared across the app: arXiv paper metadata, text chunks,
and the request/response contracts for the ingest API.

"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class Paper(BaseModel):
    """
    Pydantic schemas shared across the app: arXiv paper metadata, text chunks,
    and the request/response contracts for the ingest API.

    """

    arxiv_id: str = Field(..., description="The arXiv ID of the paper.")
    title: str = Field(..., description="The title of the paper.")
    abstract: str = Field(..., description="The abstract of the paper.")
    authors: List[str] = Field(..., description="The List of authors of the paper.")
    published: datetime = Field(..., description="The publication date of the paper.")
    updated: datetime = Field(..., description="The last updated date of the paper.")
    categories: List[str] = Field(..., description="The List of categories of the paper.")
    pdf_url: str = Field(..., description="The URL to the PDF of the paper.")


class Chunk(BaseModel):
    """
    A Single chunk of text extracted from a paper, along with its metadata.

    """

    chunk_id: str = Field(..., description="A unique identifier for the chunk.")
    paper_id: str = Field(..., description="The arXiv ID of the paper this chunk belongs to.")
    chunk_index: int = Field(..., description="The index of the chunk within the paper.")
    text: str = Field(..., description="The text content of the chunk.")
    word_count: int = Field(..., description="The number of words in the chunk.")

class IngestRequest(BaseModel):
    """
    Request schema for the ingest API.

    """

    arxiv_id: str | None = Field(default=None, description="The arXiv ID of the paper to ingest.")
    query: str | None = Field(default=None, description="A search query to find papers to ingest.")
    max_results: int = Field(default=1, ge=1, le=10, description="The maximum number of papers to ingest for a query.")


class IngestedPaper(BaseModel):
    """
    Response schema for the ingest API when ingesting a single paper.

    """

    paper: Paper = Field(..., description="The metadata of the ingested paper.")
    num_chunks: int = Field(..., description="The number of text chunks created for the paper.")

class IngestResponse(BaseModel):
    """
    Response schema for the ingest API when ingesting multiple papers.

    """

    ingested: List[IngestedPaper] = Field(..., description="The List of ingested papers and their metadata.")


class PaperSearchResult(BaseModel):
    """One paper-search hit. score is L2 distance -- lower means more similar."""

    paper: Paper
    score: float


class PaperSearchResponse(BaseModel):
    results: list[PaperSearchResult]


class ChunkSearchResult(BaseModel):
    """One chunk-search hit. score is L2 distance -- lower means more similar."""

    chunk: Chunk
    score: float


class ChunkSearchResponse(BaseModel):
    results: list[ChunkSearchResult]


class QARequest(BaseModel):
    """
    Request schema for the RAG question-answering API.

    """

    question: str = Field(..., description="The question to answer.")
    paper_id: str | None = Field(default=None, description="The arXiv ID of the paper to scope retrieval to. If None, retrieval spans all ingested papers.")
    k: int = Field(default=5, ge=1, le=20, description="The number of chunks to retrieve for answering the question.")

class QAResponse(BaseModel):
    """
    Response schema for the RAG question-answering API.

    """

    answer: str = Field(..., description="The answer to the question, grounded in the retrieved chunks.")
    sources: List[ChunkSearchResult] = Field(..., description="The List of retrieved chunks that were used to generate the answer. Each chunk includes its metadata and similarity score.")

