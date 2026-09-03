"""
Downloads a paper's PDF and extracts its text using LangChain's
PyMuPDFLoader.

Replaces the previous hand-rolled httpx + pypdf download/extract logic.
This keeps PDF handling consistent with the rest of the LangChain-based
pipeline (ArxivAPIWrapper, text splitters, FAISS) and fixes a latent bug:
the old version imported `pypdf`, which was never listed in
requirements.txt (only `pymupdf` was pinned there) -- PyMuPDFLoader uses
pymupdf under the hood, so this now actually matches what's installed.

"""

import asyncio

from langchain_community.document_loaders import PyMuPDFLoader


def _load_pdf_sync(pdf_url: str) -> str:
    """Blocking PDF download + text extraction. Runs off the event loop.

    PyMuPDFLoader (via BasePDFLoader) accepts a URL directly: it detects
    the path isn't local, downloads it to a temp file internally using
    `requests`, and cleans up after itself. We don't need to manage the
    download ourselves.
    """

    loader = PyMuPDFLoader(pdf_url)
    docs = loader.load()  

    pages_text = [doc.page_content for doc in docs]
    full_text = "\n".join(pages_text)


    full_text = "\n".join(
        line.strip() for line in full_text.splitlines() if line.strip()
    )
    return full_text


async def fetch_and_extract_text(pdf_url: str) -> str:
    """Download a PDF from a URL and return its concatenated text content.

    PyMuPDFLoader's internal download is synchronous (blocking `requests`
    call). Since this is called from async FastAPI route handlers, running
    it directly here would freeze the event loop -- and every other
    concurrent request -- for however long the PDF download takes.
    `asyncio.to_thread` offloads it to a worker thread so the event loop
    stays free to handle other requests in the meantime.
    """

    return await asyncio.to_thread(_load_pdf_sync, pdf_url)