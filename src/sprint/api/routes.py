"""HTTP routes.

Note every handler below is a plain `def`, not `async def`. FastAPI runs an
event loop: an `async` handler that makes a *blocking* call (which every
OpenAI call here is) stalls the entire server, not just that request —
health checks included. A plain `def` is moved to a worker thread
automatically, which is what blocking work needs.

Java: `async def` is the Netty event loop; plain `def` is the servlet
threadpool you are used to. Picking the wrong one only shows up under load.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from ..extraction import EmptyPdfError, ExtractionError, Invoice, extract_from_pdf
from ..llm import client
from ..settings import settings

router = APIRouter()


# ── health ───────────────────────────────────────────────────────────────────

@router.get("/health", tags=["ops"])
def health() -> dict[str, str]:
    """Liveness: is the process up? Deliberately does no real work."""
    return {"status": "ok"}


@router.get("/ready", tags=["ops"])
def ready() -> dict[str, str]:
    """Readiness: can we actually reach the model provider?

    Most health checks return 200 if the process answers — which proves
    only that the process answers. This one fails when the API key is
    wrong or the provider is down, so a load balancer stops sending work
    to an instance that cannot do any.

    Uses models.retrieve rather than a completion: it exercises auth and
    connectivity without spending tokens.
    """
    try:
        client.with_options(timeout=5.0).models.retrieve(settings.openai_model)
    except Exception as exc:  # noqa: BLE001 — any failure means not ready
        raise HTTPException(
            status_code=503,
            detail=f"model provider unreachable: {type(exc).__name__}: {exc}",
        ) from exc
    return {"status": "ready", "model": settings.openai_model}


# ── extraction (Day 3, now over HTTP) ────────────────────────────────────────

@router.post("/extract", response_model=Invoice, tags=["extraction"])
def extract(file: UploadFile = File(..., description="An invoice PDF")) -> Invoice:
    """Extract structured fields from an invoice PDF.

    `response_model=Invoice` makes the Day 3 schema do a third job: it is
    the extraction contract, the validator, AND the documented response
    shape at /docs. One definition, three uses.
    """
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "only .pdf files are accepted")

    # The extractor reads from a path, so land the upload on disk first.
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file.file.read())
        path = Path(tmp.name)

    try:
        return extract_from_pdf(path)
    except EmptyPdfError as exc:
        # The client's fault: a scan with no text layer. 422, not 500.
        raise HTTPException(422, str(exc)) from exc
    except ExtractionError as exc:
        # Our side failed after retrying. 502 — an upstream problem.
        raise HTTPException(502, str(exc)) from exc
    finally:
        path.unlink(missing_ok=True)
