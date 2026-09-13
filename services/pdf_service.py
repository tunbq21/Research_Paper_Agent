"""
PDF Service: Extracts raw text from a PDF file using PyMuPDF (fitz).
"""
from pathlib import Path

import pymupdf as fitz  # PyMuPDF (modern import)
from loguru import logger


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text content from a PDF file.

    Args:
        pdf_path: The absolute or relative path to the PDF file.

    Returns:
        A single string containing all extracted text, with pages
        separated by newlines.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        RuntimeError: If PyMuPDF fails to open or read the file.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    logger.info(f"Extracting text from PDF: {path.name}")

    try:
        doc = fitz.open(str(path))
        full_text_parts: list[str] = []

        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if text.strip():
                full_text_parts.append(text)
                logger.debug(f"  Page {page_num}: extracted {len(text)} characters")

        doc.close()
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from '{pdf_path}': {e}") from e

    full_text = "\n\n".join(full_text_parts)
    logger.info(
        f"Extraction complete. Total characters: {len(full_text)}, "
        f"Pages processed: {len(full_text_parts)}"
    )
    return full_text
