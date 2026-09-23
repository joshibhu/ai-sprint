"""Stage 1: send a menu, look at what the model asks for. Do not act on it."""

from sprint.agent.tools import WEATHER_TOOL
from sprint.llm import client
from sprint.settings import settings

messages = [
    {"role": "user", "content": "What is the temperature in Pune right now?"}
]

response = client.chat.completions.create(
    model=settings.openai_model,
    messages=messages,
    tools=[WEATHER_TOOL],          # <- the only new argument
)

message = response.choices[0].message

print("text the model wrote :", repr(message.content))
print("tools it asked for   :", message.tool_calls)
print("why it stopped       :", response.choices[0].finish_reason)
