"""Ask the agent a question from the command line.

    uv run python scripts/ask.py "which stations are in Mumbai?"

With no question, it starts a prompt loop — type questions, blank line to quit.
"""

import sys

from sprint.agent import run_agent


def main() -> None:
    if len(sys.argv) > 1:
        print(run_agent(" ".join(sys.argv[1:])))
        return

    print("Ask anything. Blank line to quit.\n")
    while True:
        try:
            question = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            break
        print(run_agent(question), "\n")


if __name__ == "__main__":
    main()
