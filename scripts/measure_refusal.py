"""Does the new system-prompt clause turn vague answers into clear refusals?

Runs the same unanswerable questions with the OLD and NEW system prompts,
N times each, and reports how often the answer is an honest refusal.

    uv run python scripts/measure_refusal.py
"""

import json

from sprint.agent.loop import SYSTEM as NEW_SYSTEM
from sprint.agent.tools import MENU, dispatch
from sprint.llm import client
from sprint.settings import settings

OLD_SYSTEM = "You are a helpful assistant. Be concise."

# Questions the three curated tools genuinely cannot answer.
QUESTIONS = [
    "Which operator has the most charging stations?",
    "What is the average price per kWh in Pune?",
    "Which stations are currently under maintenance?",
]

N = 3

# Phrases that indicate the model admitted it could not answer.
#
# NOTE: models write a CURLY apostrophe (U+2019) — "can\u2019t", not "can't".
# The first version of this list used straight quotes, matched nothing, and
# reported a confident 0/3 everywhere. A broken detector does not raise an
# error; it returns a plausible number. Normalise before matching.
REFUSAL_HINTS = ("can't", "cannot", "don't have", "do not have", "no tool",
                 "not available", "unable", "isn't available", "not something",
                 "not in my data", "no data", "don't see", "isn't something")


def normalise(text: str) -> str:
    """Lowercase, and fold curly quotes to straight ones."""
    return text.lower().replace("\u2019", "'").replace("\u2018", "'")


def ask(question: str, system: str) -> str:
    """One agent run with a given system prompt."""
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": question}]
    for _ in range(5):
        r = client.chat.completions.create(
            model=settings.openai_model, messages=messages, tools=MENU)
        m = r.choices[0].message
        if not m.tool_calls:
            return m.content or ""
        messages.append(m.model_dump(exclude_none=True))
        for c in m.tool_calls:
            messages.append({
                "role": "tool", "tool_call_id": c.id,
                "content": dispatch(c.function.name,
                                    json.loads(c.function.arguments or "{}")),
            })
    return ""


def main() -> None:
    for label, system in [("OLD (no clause)", OLD_SYSTEM),
                          ("NEW (with clause)", NEW_SYSTEM)]:
        print(f"\n═══ {label} ═══")
        for q in QUESTIONS:
            refusals = 0
            sample = ""
            for _ in range(N):
                answer = ask(q, system)
                if any(h in normalise(answer) for h in REFUSAL_HINTS):
                    refusals += 1
                sample = answer
            print(f"  {q}")
            print(f"     honest refusal {refusals}/{N}   e.g. {sample.strip().splitlines()[0][:90] if sample.strip() else '(empty)'}")


if __name__ == "__main__":
    main()
