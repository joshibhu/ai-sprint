"""Document extraction: PDF in, validated Invoice out.

The public surface of this package. Importers use
``from sprint.extraction import extract_from_pdf`` and never reach into
the modules below — so pdf/schema/service can be reorganised freely.
Java: the exported interface of a module, with the rest package-private.
"""

from .pdf import EmptyPdfError, read_text
from .schema import Invoice
from .service import ExtractionError, extract_from_pdf, extract_from_text

__all__ = [
    "EmptyPdfError",
    "ExtractionError",
    "Invoice",
    "extract_from_pdf",
    "extract_from_text",
    "read_text",
]
