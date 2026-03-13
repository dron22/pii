"""Extract text with character-level bounding boxes from PDF pages."""

from dataclasses import dataclass, field

import fitz  # pymupdf


@dataclass
class Char:
    text: str
    bbox: tuple[float, float, float, float]  # x0, y0, x1, y1
    page: int


@dataclass
class PageText:
    page_num: int
    chars: list[Char] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "".join(c.text for c in self.chars)

    @property
    def is_empty(self) -> bool:
        return not self.text.strip()


def extract(pdf_path: str, ocr: bool = False) -> list[PageText]:
    """Extract text and character bboxes from a PDF.

    For image-only pages, prints a warning unless ocr=True.
    Returns one PageText per page.
    """
    doc = fitz.open(pdf_path)
    pages = []

    for page_num, page in enumerate(doc):
        page_text = _extract_page(page, page_num)

        if page_text.is_empty:
            if ocr:
                page_text = _extract_page_ocr(page, page_num)
            else:
                import click

                click.echo(
                    f"Warning: page {page_num + 1} contains no extractable text. "
                    f"Re-run with --ocr to enable OCR for scanned pages."
                )

        pages.append(page_text)

    doc.close()
    return pages


def _extract_page(page: fitz.Page, page_num: int) -> PageText:
    """Extract characters with bboxes from a text-based PDF page."""
    page_text = PageText(page_num=page_num)

    raw = page.get_text("rawdict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
    for block in raw.get("blocks", []):
        if block.get("type") != 0:  # 0 = text block
            continue
        for line in block.get("lines", []):
            last_bbox: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
            for span in line.get("spans", []):
                for char in span.get("chars", []):
                    c = char.get("c", "")
                    bbox = tuple(char.get("bbox", (0.0, 0.0, 0.0, 0.0)))
                    if c:
                        page_text.chars.append(Char(text=c, bbox=bbox, page=page_num))
                        last_bbox = bbox
            # Add newline after each line so PII at line-end gets a word boundary
            page_text.chars.append(Char(text="\n", bbox=last_bbox, page=page_num))

    return page_text


def _extract_page_ocr(page: fitz.Page, page_num: int) -> PageText:
    """Extract text from an image-only page using Tesseract OCR."""
    try:
        import io

        import pytesseract
        from PIL import Image
    except ImportError:
        import click

        click.echo(
            "Error: OCR dependencies not installed. Run: pip install pytesseract pillow",
            err=True,
        )
        return PageText(page_num=page_num)

    page_text = PageText(page_num=page_num)

    # Render page to image at 300 DPI for good OCR quality
    mat = fitz.Matrix(300 / 72, 300 / 72)
    pix = page.get_pixmap(matrix=mat)
    img = Image.open(io.BytesIO(pix.tobytes("png")))

    # Get word-level bboxes from Tesseract (hOCR-style data)
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    scale_x = page.rect.width / img.width
    scale_y = page.rect.height / img.height

    for i, word in enumerate(data["text"]):
        if not word.strip():
            continue
        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
        # Convert image coords to PDF points
        x0, y0 = x * scale_x, y * scale_y
        x1, y1 = (x + w) * scale_x, (y + h) * scale_y
        # Treat each word as a sequence of chars sharing the word bbox
        for char in word:
            page_text.chars.append(Char(text=char, bbox=(x0, y0, x1, y1), page=page_num))

    return page_text
