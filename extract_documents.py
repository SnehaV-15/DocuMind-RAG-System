"""Extract text from PDFs, Markdown and TXT files.
PDF pages with selectable text use PyMuPDF. Scanned/image-only pages use EasyOCR.
"""
from pathlib import Path
import pymupdf
import easyocr
import numpy as np
from PIL import Image

from config import DOCUMENTS_DIR, EXTRACTED_DIR

SUPPORTED_TEXT = {".txt", ".md", ".markdown"}
OCR_READER = None


def get_ocr_reader():
    global OCR_READER
    if OCR_READER is None:
        print("Loading EasyOCR (first run may download language data)...")
        OCR_READER = easyocr.Reader(["en"], gpu=False)
    return OCR_READER


def extract_pdf(pdf_path: Path) -> str:
    pdf = pymupdf.open(pdf_path)
    page_texts = []

    for page_index, page in enumerate(pdf):
        text = page.get_text("text").strip()

        # If the page has almost no selectable text, treat it as scanned.
        if len(text) < 40:
            print(f"  Page {page_index + 1}: OCR")
            pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            results = get_ocr_reader().readtext(np.array(image), detail=0, paragraph=True)
            text = "\n".join(results).strip()
        else:
            print(f"  Page {page_index + 1}: direct text extraction")

        if text:
            page_texts.append(f"[Source: {pdf_path.name}, page {page_index + 1}]\n{text}")

    pdf.close()
    return "\n\n".join(page_texts)


def main():
    DOCUMENTS_DIR.mkdir(exist_ok=True)
    EXTRACTED_DIR.mkdir(exist_ok=True)

    inputs = sorted(
        p for p in DOCUMENTS_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in {".pdf", *SUPPORTED_TEXT}
    )

    if not inputs:
        print("No PDF, TXT or Markdown files found in documents/.")
        return

    total_chars = 0
    for path in inputs:
        print(f"\nProcessing {path.name}")
        if path.suffix.lower() == ".pdf":
            content = extract_pdf(path)
        else:
            content = path.read_text(encoding="utf-8", errors="ignore")

        output = EXTRACTED_DIR / f"{path.stem}.txt"
        output.write_text(content, encoding="utf-8")
        total_chars += len(content)
        print(f"Saved {output.name}: {len(content):,} characters")

    print(f"\nFinished. Total extracted characters: {total_chars:,}")
    print("Open extracted_docs/ and inspect the text before ingestion.")


if __name__ == "__main__":
    main()
