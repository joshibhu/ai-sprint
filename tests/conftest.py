"""Shared test fixtures — chiefly, a fake model.

The model is the one part of this system that cannot be tested: it costs
money, it needs a network, and it gives a different answer each run (10/10
then 9/10 on Day 3; 0/5 then 5/5 on Day 5).

So we do not test it. We REPLACE it, and test our own code — the
dispatcher, the SQL, the loop's exit conditions, the parsing. Those are
deterministic, and they are where the bugs actually are.

Java: a Mockito stub for the one collaborator you do not own.
"""

import json
from typing import Any

import pytest
from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageFunctionToolCall,
)
from openai.types.chat.chat_completion_message_function_tool_call import Function


# ── building blocks: what a scripted model turn can be ──────────────────────

def says(text: str) -> ChatCompletionMessage:
    """A plain answer, no tool wanted. The loop should return this."""
    return ChatCompletionMessage(role="assistant", content=text)


def wants(*calls: tuple[str, dict[str, Any]]) -> ChatCompletionMessage:
    """A turn requesting one or more tools.

    `wants(("get_weather", {"city": "Pune"}))` mimics exactly what the real
    API returns: no text, and arguments as a JSON *string*, not a dict.
    """
    return ChatCompletionMessage(
        role="assistant",
        content=None,
        tool_calls=[
            ChatCompletionMessageFunctionToolCall(
                id=f"call_{i}",
                type="function",
                function=Function(name=name, arguments=json.dumps(args)),
            )
            for i, (name, args) in enumerate(calls)
        ],
    )


# ── the fake client ─────────────────────────────────────────────────────────

class _Choice:
    def __init__(self, message): self.message = message


class _Response:
    def __init__(self, message):
        self.choices = [_Choice(message)]
        self.usage = None


class FakeModel:
    """Stands in for `client`. Replays a scripted list of turns.

    Also records every request, so tests can assert on what was SENT —
    which is how we check the tool results were fed back correctly.
    """

    def __init__(self, script: list[ChatCompletionMessage]):
        self._script = list(script)
        self.requests: list[dict] = []
        self.chat = self                      # client.chat.completions.create
        self.completions = self

    def create(self, **kwargs) -> _Response:
        self.requests.append(kwargs)
        if not self._script:
            raise AssertionError(
                "the loop asked the model more times than the script allows"
            )
        return _Response(self._script.pop(0))


@pytest.fixture
def fake_model(monkeypatch):
    """Install a scripted model into the agent loop.

        def test_x(fake_model):
            fake_model([wants(("calculate", {"expression": "2+2"})),
                        says("It is 4.")])
    """
    def install(script: list[ChatCompletionMessage]) -> FakeModel:
        fake = FakeModel(script)
        monkeypatch.setattr("sprint.agent.loop.client", fake)
        return fake

    return install
