"""The only module that imports the OpenAI SDK."""

from collections.abc import Callable
from dataclasses import dataclass

from openai import OpenAI

from .settings import settings

# One client for the app, like a singleton WebClient (it pools connections).
# `api_key=` is required: the SDK's `*` makes those params keyword-only.
client = OpenAI(api_key=settings.openai_api_key)

Message = dict[str, str]

@dataclass
class TurnResult:
    """Everything one assistant turn produced."""

    text: str
    input_tokens: int
    output_tokens: int
    # Billed as output, never returned. 0 on non-reasoning models.
    reasoning_tokens: int = 0

def stream_turn(
    messages: list[Message],
    on_chunk: Callable[[str], None],
) -> TurnResult:
    """Stream one assistant turn.

    Calls `on_chunk` with each fragment as it arrives; returns the assembled
    reply and token usage once the stream is exhausted.
    """
    stream = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
    )

    parts: list[str] = []
    input_tokens = output_tokens = reasoning_tokens = 0

    for chunk in stream:
        # The usage chunk arrives last and has an EMPTY choices list,
        # so read usage before touching choices[0].
        if chunk.usage is not None:
            input_tokens = chunk.usage.prompt_tokens
            output_tokens = chunk.usage.completion_tokens
            # Absent entirely on non-reasoning models — getattr, not [].
            details = chunk.usage.completion_tokens_details
            reasoning_tokens = getattr(details, "reasoning_tokens", 0) or 0
        if not chunk.choices:
            continue

        piece = chunk.choices[0].delta.content
        if piece:                      # None on the role chunk and at the end
            parts.append(piece)
            on_chunk(piece)

    return TurnResult(
        "".join(parts), input_tokens, output_tokens, reasoning_tokens
    )


def complete(prompt: str) -> str:
    """Send one prompt to the model, return the reply text."""
    # Blocking HTTP call, like RestTemplate. (AsyncOpenAI is the asyncio twin.)
    response = client.chat.completions.create(
        model=settings.openai_model,
        # Dict literal = Map.of(...); dicts model loose JSON instead of a class.
        messages=[{"role": "user", "content": prompt}],
    )
    # .content is `str | None`; `or ""` picks the first truthy operand, so the
    # declared `-> str` stays honest. Java: requireNonNullElse(content, "").
    return response.choices[0].message.content or ""
