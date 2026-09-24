"""The dispatcher — the security boundary. No model, no network, no database.

These are the fastest and most important tests in the suite: they pin the
behaviour that stops a fooled model doing damage.
"""

from sprint.agent import MENU, TOOLS, dispatch


def test_menu_and_dispatcher_agree():
    """Every offered tool must be runnable, and nothing extra registered.

    A name in the menu but not in TOOLS = the model asks for something that
    errors. A name in TOOLS but not the menu = a capability nobody reviewed.
    """
    offered = {m["function"]["name"] for m in MENU}
    runnable = set(TOOLS)
    assert offered == runnable


def test_unknown_tool_is_refused_not_executed():
    """The core guarantee: a name absent from TOOLS cannot run."""
    result = dispatch("delete_all_stations", {})
    assert "no such tool" in result.lower()
    assert "delete_all_stations" in result


def test_dispatch_never_raises_on_bad_arguments():
    """A broken call must come back as text the model can recover from.

    An exception here would kill the whole conversation; a message lets the
    model apologise or try something else.
    """
    result = dispatch("get_weather", {"wrong_argument": 1})
    assert "error" in result.lower()


def test_calculate_runs_real_arithmetic():
    assert dispatch("calculate", {"expression": "4320 * 0.15"}).startswith("648")


def test_calculate_refuses_anything_that_is_not_arithmetic():
    """eval() would run all of these. The AST allow-list does not."""
    hostile = [
        "__import__('os').getcwd()",
        "open('.env').read()",
        "1 if True else 2",
        "[x for x in range(10)]",
    ]
    for expression in hostile:
        result = dispatch("calculate", {"expression": expression})
        assert "error" in result.lower(), f"LEAKED: {expression}"
