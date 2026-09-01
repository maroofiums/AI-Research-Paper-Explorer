import fitz

from app.services.pdf_extractor import extract_pdf_text


def test_extract_pdf_text(tmp_path):
    pdf_path = tmp_path / "test.pdf"

    document = fitz.open()

    page = document.new_page()
    page.insert_text(
        (50, 50),
        "PaperMind PDF extraction test."
    )

    document.save(pdf_path)
    document.close()

    pages = extract_pdf_text(str(pdf_path))

    assert len(pages) == 1
    assert pages[0]["page_number"] == 1
    assert "PaperMind PDF extraction test." in pages[0]["text"]