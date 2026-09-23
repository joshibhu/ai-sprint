"""Stage 2: act on the request, feed the result back, get a real answer.

KEPT AS A LEARNING STEP, AND IT HAS A KNOWN FLAW.

Line 27 calls get_weather() directly, ignoring the name the model sent
back. With one tool that is right by luck; with two it silently runs the
wrong one. The fix is a lookup table keyed by name — see dispatch() in
sprint/agent/tools.py. That dictionary is the security boundary: a name
that is not in it cannot run, however the model came to ask for it.
"""

import json

from sprint.agent.tools import WEATHER_TOOL, get_weather
from sprint.llm import client
from sprint.settings import settings

messages = [
    {"role": "user", "content": "What is the temperature in Pune right now?"}
]

# ---- round 1: the model asks -------------------------------------------
first = client.chat.completions.create(
    model=settings.openai_model,
    messages=messages,
    tools=[WEATHER_TOOL],
)
message = first.choices[0].message

# The model's request goes back into the conversation, unchanged.
messages.append(message.model_dump(exclude_none=True))

# ---- we do the work ----------------------------------------------------
call = message.tool_calls[0]
args = json.loads(call.function.arguments)     # string -> dict
result = get_weather(**args)                   # OUR code runs. Not the model's.

print("the model asked for :", call.function.name, args)
print("our function returned:", result)

# The result goes back as a new message, quoting the ticket number.
messages.append({
    "role": "tool",
    "tool_call_id": call.id,
    "content": result,
})

# ---- round 2: the model answers ----------------------------------------
second = client.chat.completions.create(
    model=settings.openai_model,
    messages=messages,
    tools=[WEATHER_TOOL],
)

print("\nfinal answer:", second.choices[0].message.content)
print("\nthe conversation is now", len(messages) + 1, "messages long")
