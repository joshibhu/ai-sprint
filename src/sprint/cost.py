"""Token cost arithmetic. No I/O, no SDK — just numbers."""
from .settings import settings


def usd_for(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens / 1_000_000 * settings.usd_per_1m_input
        + output_tokens / 1_000_000 * settings.usd_per_1m_output
    )


def inr_for(input_tokens: int, output_tokens: int) -> float:
    return usd_for(input_tokens, output_tokens) * settings.usd_to_inr
