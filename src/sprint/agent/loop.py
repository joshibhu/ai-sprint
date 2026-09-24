"""The agent loop. Ask, run tools, ask again, until the model answers."""

import json

from ..llm import client
from ..settings import settings
from .tools import MENU, dispatch

MAX_ROUNDS = 5     # a confused model loops forever, and you pay per lap

# NOTE: an earlier "prefer calling a tool over your own knowledge" system
# prompt was removed. Measured over 5 runs it only nudged tool use 2/5,
# while the tool DESCRIPTION alone achieved 5/5 — and the blunt instruction
# made answers worse, stripping useful general knowledge out of them.
# The clause below is NOT that instruction returning. That one pushed tool
# use everywhere. This one is scoped to station data and does not add
# capability — it converts a vague non-answer into a clear refusal, which is
# the difference between a user knowing the system failed and not knowing.
SYSTEM = (
    "You are a helpful assistant. Be concise.\n"
    "Facts about charging stations come ONLY from the tools provided. If no "
    "tool can answer a question about stations, say so plainly and name what "
    "you can answer instead. Never answer a station question from your own "
    "knowledge, and never guess."
)


def run_agent(question: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]

    for _ in range(MAX_ROUNDS):
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=MENU,
        )
        message = response.choices[0].message

        # No tool wanted -> it answered. This is the normal exit.
        if not message.tool_calls:
            return message.content or ""

        # Replay the request into the history.
        messages.append(message.model_dump(exclude_none=True))

        # It may ask for SEVERAL tools at once. Every one needs a reply.
        for call in message.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            print(f"   [running {call.function.name}({args})]")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": dispatch(call.function.name, args),
            })

    return f"Gave up after {MAX_ROUNDS} rounds."
