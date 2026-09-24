"""The agent loop, with a scripted model. Fast, free, deterministic."""

from conftest import says, wants

from sprint.agent import MAX_ROUNDS, run_agent


def test_plain_answer_needs_no_tools(fake_model):
    """The normal exit. Beginners treat this as an error case and break
    every simple question."""
    fake_model([says("Paris.")])
    assert run_agent("Capital of France?") == "Paris."


def test_tool_result_is_fed_back_and_used(fake_model):
    fake = fake_model([
        wants(("calculate", {"expression": "2+2"})),
        says("It is 4."),
    ])
    assert run_agent("What is 2+2?") == "It is 4."

    # Two requests: the question, then the question plus the tool result.
    assert len(fake.requests) == 2

    # The SECOND request must carry the assistant's own tool request back
    # (Day 6: without it the API rejects the tool message with a 400),
    # followed by the result, tied by id.
    sent = fake.requests[1]["messages"]
    roles = [m["role"] for m in sent]
    assert roles == ["system", "user", "assistant", "tool"]
    assert sent[3]["content"].startswith("4")
    assert sent[3]["tool_call_id"] == sent[2]["tool_calls"][0]["id"]


def test_several_tools_in_one_turn_all_get_replies(fake_model):
    """The model can ask for two things at once. Every request needs a
    matching result or the next call is rejected."""
    fake = fake_model([
        wants(("calculate", {"expression": "1+1"}),
              ("calculate", {"expression": "2+2"})),
        says("2 and 4."),
    ])
    run_agent("one plus one, and two plus two?")

    sent = fake.requests[1]["messages"]
    tool_messages = [m for m in sent if m["role"] == "tool"]
    assert len(tool_messages) == 2
    assert {m["tool_call_id"] for m in tool_messages} == {"call_0", "call_1"}


def test_loop_gives_up_instead_of_running_forever(fake_model):
    """A confused model must not ping-pong indefinitely — every lap is a
    paid API call with a growing history."""
    fake_model([wants(("calculate", {"expression": "1+1"}))] * MAX_ROUNDS)

    answer = run_agent("loop forever please")

    assert "gave up" in answer.lower()
    assert str(MAX_ROUNDS) in answer


def test_the_menu_is_sent_on_every_request(fake_model):
    """The API is stateless — the tool list is not remembered between calls."""
    fake = fake_model([
        wants(("calculate", {"expression": "1+1"})),
        says("2."),
    ])
    run_agent("one plus one?")

    assert all("tools" in request for request in fake.requests)


def test_unknown_tool_does_not_crash_the_conversation(fake_model):
    """If the model hallucinates a tool name, the loop keeps going and the
    model is told what went wrong."""
    fake = fake_model([
        wants(("drop_everything", {})),
        says("Sorry, I cannot do that."),
    ])
    answer = run_agent("delete it all")

    assert answer == "Sorry, I cannot do that."
    tool_reply = [m for m in fake.requests[1]["messages"] if m["role"] == "tool"][0]
    assert "no such tool" in tool_reply["content"].lower()
