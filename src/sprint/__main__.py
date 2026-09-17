import sys

from .llm import complete


def main() -> None:
    # argv[0] is the program name, so real args start at 1 (Java's start at 0).
    if len(sys.argv) < 2:
        print("usage: sprint \"your prompt here\"", file=sys.stderr)
        raise SystemExit(2)  # == System.exit(2), but it's a catchable exception

    # Separator is the object: " ".join(list) vs Java String.join(" ", list).
    prompt = " ".join(sys.argv[1:])
    print(complete(prompt))


# True only when run as a script (`python -m sprint`) — guards against an import
# firing an API call. `uv run sprint` skips this and calls main() directly.
if __name__ == "__main__":
    main()
