import sys

from .cost import inr_for
from .llm import Message, stream_turn
from .settings import settings


SYSTEM_PROMPT = "You are a concise, helpful assistant. Prefer short answers."


def _turn(messages: list[Message]) -> float:
    """Stream one turn, append the reply, print the cost line. Returns ₹."""
    print("bot> ", end="", flush=True)
    result = stream_turn(
        messages,
        on_chunk=lambda piece: print(piece, end="", flush=True),
    )
    print()

    messages.append({"role": "assistant", "content": result.text})

    inr = inr_for(result.input_tokens, result.output_tokens)
    print(
        f"     in={result.input_tokens} out={result.output_tokens}"
        f" (reasoning {result.reasoning_tokens}) ₹{inr:.4f}\n",
        file=sys.stderr,
    )
    return inr


def chat() -> None:
    messages: list[Message] = [{"role": "system", "content": SYSTEM_PROMPT}]
    total = 0.0

    print(f"model: {settings.openai_model}   (type 'exit' to quit)\n")

    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user in {"exit", "quit"}:
            break
        if not user:
            continue

        messages.append({"role": "user", "content": user})
        total += _turn(messages)

    print(f"session total: ₹{total:.4f}", file=sys.stderr)


def one_shot(prompt: str) -> None:
    messages: list[Message] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    _turn(messages)


def main() -> None:
    if len(sys.argv) > 1:
        one_shot(" ".join(sys.argv[1:]))
    else:
        chat()


if __name__ == "__main__":
    main()
