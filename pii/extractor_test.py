"""Tests for PDF text extraction."""

from pathlib import Path

import pytest

from pii.extractor import PageText, extract

TESTDATA = Path(__file__).parent / "testdata"
INVOICE_PDF = TESTDATA / "sample_hospital_invoice_synthetic.pdf"
SCANNED_PDF = TESTDATA / "sample_scanned_admission_form_synthetic.pdf"


@pytest.mark.skipif(not INVOICE_PDF.exists(), reason="Sample PDF not found")
def test_extract_returns_pages():
    pages = extract(str(INVOICE_PDF))
    assert len(pages) > 0
    assert all(isinstance(p, PageText) for p in pages)


@pytest.mark.skipif(not INVOICE_PDF.exists(), reason="Sample PDF not found")
def test_extract_text_content():
    pages = extract(str(INVOICE_PDF))
    full_text = "".join(p.text for p in pages)
    assert "Lara Meier" in full_text
    assert "756" in full_text  # AHV number prefix


@pytest.mark.skipif(not INVOICE_PDF.exists(), reason="Sample PDF not found")
def test_extract_chars_have_valid_bboxes():
    pages = extract(str(INVOICE_PDF))
    for page in pages:
        for char in page.chars:
            x0, y0, x1, y1 = char.bbox
            assert x1 >= x0
            assert y1 >= y0


@pytest.mark.skipif(not SCANNED_PDF.exists(), reason="Scanned PDF not found")
def test_scanned_page_warns_without_ocr(capsys):
    pages = extract(str(SCANNED_PDF), ocr=False)
    captured = capsys.readouterr()
    has_warning = "Warning" in captured.out
    all_empty = all(p.is_empty for p in pages)
    # If all pages are empty (truly image-only), a warning must have been shown.
    # If the PDF has an embedded text layer, pages will have content — no warning needed.
    assert has_warning or not all_empty
