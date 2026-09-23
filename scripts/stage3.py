"""Stage 3: the loop. One tool, but questions that need it more than once."""

from sprint.agent.loop import run_agent

for question in [
    "Is it warmer in Pune or Bengaluru right now?",
    "What is the capital of France?",
    "I like a cooler place hence I need to decide among Mussorie and Manali, where to go ?",
]:
    print(f"\nQ: {question}")
    print(f"A: {run_agent(question)}")
