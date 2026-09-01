from pathlib import Path

import fitz


def extract_pdf_text(file_path: str) -> list[dict]:
    """
    Extract text from a PDF page by page.

    Returns:
        A list containing page number and extracted text.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {file_path}"
        )

    pages = []

    with fitz.open(path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if not text:
                continue

            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                }
            )

    return pages