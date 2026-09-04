"""
Wrapper around LangChain's ArxivAPIWrapper, translating its Document output
into our own `Paper` schema so the rest of the app never has to reason about
LangChain's Document/metadata shape directly.
 
Why we call ArxivAPIWrapper ourselves instead of using ArxivLoader directly:
`ArxivLoader` (langchain_community.document_loaders.ArxivLoader) is a thin
`BaseLoader` shim around this same wrapper's `.load()` method. Using the
wrapper directly gives us the identical LangChain-managed fetch/parse logic,
but lets us own the mapping from its metadata dict onto our own `Paper`
model so if LangChain changes its internal Document shape in a future
version, only this one file needs to change, not every caller downstream.

"""

import re
from typing import List

from langchain_community.document_loaders import ArxivAPIWrapper

from app.models.schemas import Paper


_ARXIV_ID_PATTERN = re.compile(r"(\d{4}\.\d{4,5})")  

_wrapper = ArxivAPIWrapper(
    load_max_docs=5,
    load_all_available_metadata=True,
    doc_content_chars_max=None,
)


def _document_to_paper(doc) -> Paper:

    """
    Convert one LangChain Document into our own Paper schema.

    """ 

    meta = doc.metadata
    
    entry_id = meta.get("entry_id", "")
    match = _ARXIV_ID_PATTERN.search(entry_id)

    if not match:
        raise ValueError(f"Could not extract arXiv ID from entry_id: {entry_id}")

    arxiv_id = match.group(1)

    return Paper(
        arxiv_id=arxiv_id,
        title=" ".join(meta["Title"].split()),
        abstract=" ".join(meta["Summary"].split()),
        authors=[name.strip() for name in meta["Authors"].split(",")],
        published=meta.get("published_first_time", meta["published"]),
        updated=meta["published"],
        categories=meta.get("categories", []),
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    )


def fetch_by_id(arxiv_id: str) -> Paper:
    """
    Fetch a single paper by its arXiv ID.

    """
    docs = _wrapper.load(arxiv_id=arxiv_id)
    
    if not docs:
        raise ValueError(f"No paper found for arXiv ID: {arxiv_id}")

    return _document_to_paper(docs[0])


def search(query: str, max_results: int = 1) -> List[Paper]:
    """Search arXiv and return the top matching papers.
 
    Builds a fresh ArxivAPIWrapper per call rather than mutating the shared
    module-level `_wrapper`'s `load_max_docs`. FastAPI handles requests
    concurrently, so mutating shared state here would let one request's
    max_results leak into a concurrent request's search — a race condition
    that would only surface under real concurrent load, not casual testing.
    """

    wrapper = ArxivAPIWrapper(
        load_max_docs=max_results,
        load_all_available_metadata=True,
        doc_content_chars_max=None,
    )

    docs = wrapper.load(query=query, max_results=max_results)
    
    return [_document_to_paper(doc) for doc in docs]
