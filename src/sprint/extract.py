"""Text -> validated Invoice, with a timeout and exactly one retry."""

import logging
from pathlib import Path

from openai import APIError

from .llm import client            # reuse the one client from Day 1
from .pdf import read_text
from .schema import Invoice
from .settings import settings

log = logging.getLogger(__name__)

TIMEOUT_SECONDS = 30.0
MAX_ATTEMPTS = 2

SYSTEM = (
    "You extract structured data from invoice documents. "
    "Use only values that appear in the document. "
    "Never invent or guess a value that is not present."
)


class ExtractionError(RuntimeError):
    """The model could not produce a usable Invoice for this document."""


def extract_from_text(text: str, *, source: str = "<text>") -> Invoice:
    """Ask the model for an Invoice. Retries once, then fails loudly.

    Never returns a partial or defaulted object — that's the whole point.
    A caller either gets real data or an exception naming the file.
    """
    last_error: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            # with_options() clones the client for this call only —
            # like .mutate() on a Spring WebClient.
            completion = client.with_options(
                timeout=TIMEOUT_SECONDS
            ).chat.completions.parse(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": text},
                ],
                response_format=Invoice,   # <- the constraint, not a request
            )

            message = completion.choices[0].message

            if message.refusal:
                raise ExtractionError(f"model refused: {message.refusal}")
            if message.parsed is None:
                raise ExtractionError("model returned no parsed object")

            return message.parsed

        # APIError covers timeouts, rate limits and 5xx. A production version
        # would distinguish retryable from not; two attempts is enough today.
        except (APIError, ExtractionError) as exc:
            last_error = exc
            log.warning(
                "%s: attempt %d/%d failed: %s", source, attempt, MAX_ATTEMPTS, exc
            )

    raise ExtractionError(
        f"{source}: gave up after {MAX_ATTEMPTS} attempts"
    ) from last_error


def extract_from_pdf(path: Path) -> Invoice:
    """Read a PDF and extract it. Convenience wrapper over the two steps."""
    return extract_from_text(read_text(path), source=path.name)
