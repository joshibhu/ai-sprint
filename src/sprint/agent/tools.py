"""Things the model may ask us to do.

Nothing here knows about the model. These are ordinary functions —
the kind you would write anyway.
"""

import httpx

TIMEOUT = 10.0


def get_weather(city: str) -> str:
    """Current temperature and wind for a city."""
    # open-meteo is free and needs no API key.
    # Step 1: turn a city name into coordinates.
    geo = httpx.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1},
        timeout=TIMEOUT,
    ).json()

    hits = geo.get("results") or []
    if not hits:
        return f"No city found matching {city!r}."

    place = hits[0]

    # Step 2: coordinates -> current conditions.
    now = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,wind_speed_10m",
        },
        timeout=TIMEOUT,
    ).json()["current"]

    return (
        f"{place['name']}: {now['temperature_2m']}°C, "
        f"wind {now['wind_speed_10m']} km/h, at {now['time']}"
    )


# The menu. This is what the model is TOLD it may ask for.
# It is plain data — a description of the function above, not the function.
WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": (
            "Current temperature and wind for a city. Use this whenever a "
            "question involves how warm, cool, hot or cold a place is — "
            "including comparisons between places."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, e.g. 'Pune' or 'Bengaluru'.",
                }
            },
            "required": ["city"],
        },
    },
}


# ── tool 2: arithmetic ──────────────────────────────────────────────────────
# NEVER eval() a string from the model — that is arbitrary code execution.
# Parse to a syntax tree and walk only an ALLOW-LIST of node types.

import ast
import operator

_ALLOWED = {
    ast.Add: operator.add,      ast.Sub: operator.sub,
    ast.Mult: operator.mul,     ast.Div: operator.truediv,
    ast.Pow: operator.pow,      ast.Mod: operator.mod,
    ast.USub: operator.neg,     ast.UAdd: operator.pos,
}


def _walk(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED:
        return _ALLOWED[type(node.op)](_walk(node.left), _walk(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED:
        return _ALLOWED[type(node.op)](_walk(node.operand))
    raise ValueError(f"not allowed: {type(node).__name__}")


def calculate(expression: str) -> str:
    """Work out an arithmetic expression."""
    return str(_walk(ast.parse(expression, mode="eval").body))


CALCULATE_TOOL = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": (
            "Work out an arithmetic expression and return the number. "
            "ALWAYS use this for any arithmetic, however simple — your own "
            "mental arithmetic is unreliable."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "e.g. '4320 * 0.15'. Digits and + - * / ( ) only.",
                }
            },
            "required": ["expression"],
        },
    },
}


from .stations import STATION_MENU, STATION_TOOLS


# What the code will ACTUALLY run. The model can name anything;
# only what is in this dictionary can happen.
TOOLS = {
    "get_weather": get_weather,
    "calculate": calculate,
    **STATION_TOOLS,
}

MENU = [WEATHER_TOOL, CALCULATE_TOOL, *STATION_MENU]


def dispatch(name: str, args: dict) -> str:
    """Run one requested tool, by name. Never raises."""
    fn = TOOLS.get(name)
    if fn is None:
        return f"Error: no such tool {name!r}. Available: {sorted(TOOLS)}"
    try:
        return fn(**args)
    except Exception as exc:
        return f"Error running {name}: {exc}"
