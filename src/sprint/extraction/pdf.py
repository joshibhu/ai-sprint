"""PDF -> plain text. No model here on purpose.

Keeping extraction separate means a bad result is attributable: either the
text was wrong, or the model was. Debugging both at once is misery.
"""

from pathlib import Path

from pypdf import PdfReader

# Below this, assume there's no real text layer.
MIN_USABLE_CHARS = 100


class EmptyPdfError(RuntimeError):
    """A PDF with no usable text — almost always a scan that needs OCR."""


def read_text(path: Path) -> str:
    """Return all text in the PDF, or raise. Never returns an empty string."""
    reader = PdfReader(str(path))

    # extract_text() returns None on a page with no text — hence `or ""`.
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    if len(text.strip()) < MIN_USABLE_CHARS:
        raise EmptyPdfError(
            f"{path.name}: only {len(text.strip())} chars of text. "
            "Probably a scanned image; that needs OCR, which we don't do here."
        )
    return text