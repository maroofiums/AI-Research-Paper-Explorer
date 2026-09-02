"""
Downloads a paper's PDF and extracts its raw text.

This is intentionally simple for Phase 1: page-by-page text extraction with
pypdf, concatenated into one string. Layout-aware parsing (figures, tables,
multi-column reflow) is a known weak point of pypdf and can be revisited
later if extraction quality turns out to matter for RAG results.
"""

import io

import httpx
from pypdf import PdfReader


async def fetch_and_extract_text(pdf_url: str) -> str:
    """Download a PDF from a URL and return its concatenated text content."""

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(pdf_url)
        response.raise_for_status()

    reader = PdfReader(io.BytesIO(response.content))

    pages_text = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages_text.append(text)

    full_text = "\n".join(pages_text)

    # Collapse repeated whitespace left over from PDF extraction (column
    # breaks, hyphenation artifacts, etc.) without destroying paragraph
    # structure entirely.
    full_text = "\n".join(line.strip() for line in full_text.splitlines() if line.strip())

    return full_text
