from openai import OpenAI

# Leading dot = relative import ("settings in MY package"), not a global lookup.
from .settings import settings

# One client for the app, like a singleton WebClient (it pools connections).
# `api_key=` is required: the SDK's `*` makes those params keyword-only.
client = OpenAI(api_key=settings.openai_api_key)


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
