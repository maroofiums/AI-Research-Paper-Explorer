"""
Client for the arXiv API (http://export.arxiv.org/api/query).

arXiv returns an Atom XML feed. We fetch it with httpx and parse it with
feedparser, which understands Atom natively and saves us from hand-rolling
XML parsing.
"""

import re

import feedparser
import httpx

from app.config import settings
from app.models.schemas import Paper

# arXiv entry IDs look like "http://arxiv.org/abs/2401.12345v2" — we want
# just "2401.12345" (version-stripped) as our canonical paper ID.
_ARXIV_ID_PATTERN = re.compile(r"arxiv\.org/abs/([^v]+)")


def _entry_to_paper(entry: feedparser.FeedParserDict) -> Paper:
    """Convert one feedparser Atom entry into our Paper schema."""

    match = _ARXIV_ID_PATTERN.search(entry.id)
    if not match:
        raise ValueError(f"Could not parse arXiv ID from entry id: {entry.id}")
    arxiv_id = match.group(1)

    pdf_url = next(
        (link.href for link in entry.links if link.get("title") == "pdf"),
        None,
    )
    if pdf_url is None:
        raise ValueError(f"No PDF link found for arXiv paper {arxiv_id}")

    return Paper(
        arxiv_id=arxiv_id,
        title=" ".join(entry.title.split()),  # collapse newlines/whitespace
        abstract=" ".join(entry.summary.split()),
        authors=[author.name for author in entry.authors],
        published=entry.published,
        updated=entry.updated,
        categories=[tag.term for tag in entry.tags],
        pdf_url=pdf_url,
    )


async def fetch_by_id(arxiv_id: str) -> Paper:
    """Fetch a single paper by its arXiv ID (e.g. '2401.12345')."""

    async with httpx.AsyncClient() as client:
        response = await client.get(
            settings.arxiv_api_base_url,
            params={"id_list": arxiv_id},
        )
        response.raise_for_status()

    feed = feedparser.parse(response.text)
    if not feed.entries:
        raise ValueError(f"No paper found for arXiv ID '{arxiv_id}'")

    return _entry_to_paper(feed.entries[0])


async def search(query: str, max_results: int = 1) -> list[Paper]:
    """Search arXiv and return the top matching papers."""

    async with httpx.AsyncClient() as client:
        response = await client.get(
            settings.arxiv_api_base_url,
            params={
                "search_query": f"all:{query}",
                "max_results": max_results,
                "sortBy": "relevance",
            },
        )
        response.raise_for_status()

    feed = feedparser.parse(response.text)
    return [_entry_to_paper(entry) for entry in feed.entries]
