"""Curated queries over the stations table.

Each function answers a whole question, not "read me a table". The SQL is
written here, in advance, reviewed. The model only supplies a parameter —
it never sees or writes SQL.
"""

from ..db import query


def find_stations_in_city(city: str) -> str:
    """Charging stations in a given city."""
    rows = query(
        """
        SELECT name, operator, connector_type, power_kw, connectors, status
        FROM stations
        WHERE lower(city) = lower(%s)
        ORDER BY power_kw DESC
        """,
        (city,),
    )
    if not rows:
        return f"No stations found in {city!r}."
    lines = [
        f"- {r['name']} ({r['operator']}): {r['connector_type']}, "
        f"{r['power_kw']}kW x{r['connectors']}, {r['status']}"
        for r in rows
    ]
    return f"{len(rows)} stations in {city}:\n" + "\n".join(lines)


def city_summary() -> str:
    """How many stations and connectors each city has. No arguments."""
    rows = query(
        """
        SELECT city,
               COUNT(*)                AS stations,
               SUM(connectors)         AS connectors,
               ROUND(AVG(power_kw), 1) AS avg_power_kw
        FROM stations
        GROUP BY city
        ORDER BY stations DESC, city
        """
    )
    lines = [
        f"- {r['city']}: {r['stations']} stations, "
        f"{r['connectors']} connectors, avg {r['avg_power_kw']}kW"
        for r in rows
    ]
    return "Stations by city:\n" + "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────
# YOUR TURN — tool 3.
#
# Copy the shape of find_stations_in_city above and change the middle:
#
#   SELECT      name, operator, city, power_kw, connectors
#   FROM        stations
#   WHERE       power_kw >= %s          <- the parameter
#     AND       status = 'live'         <- a planned site is no use today
#   ORDER BY    power_kw DESC
#
# Then: return a sentence if there are no rows, and one line per row
# otherwise. Delete the `raise` when you have written it.
# ─────────────────────────────────────────────────────────────────────────

def find_fast_chargers(min_power_kw: float) -> str:
    """Stations that can charge at or above a given power, in kW.

    Only stations currently IN SERVICE are returned — planned sites and
    those under maintenance are excluded, since a driver cannot use them.
    """
    rows = query(
        """
        SELECT name, operator, city, power_kw, connectors
        FROM stations
        WHERE  power_kw >= %s   
        AND  status = 'live'   
        ORDER BY power_kw DESC
        """,
        (min_power_kw,),
    )
    if not rows:
        return f"No in-service stations at {min_power_kw}kW or more."
    lines = [
        f"- {r['name']} ({r['operator']}): {r['city']}, "
        f"{r['power_kw']}kW x{r['connectors']}"
        for r in rows
    ]
    return (
        f"{len(rows)} in-service stations at {min_power_kw}kW or more:\n"
        + "\n".join(lines)
    )


# ── menu entries ────────────────────────────────────────────────────────────
# Descriptions are prompt text (Day 3, Day 5). "Use this when..." is what
# makes a tool fire; "what it does" alone is not enough.

FIND_IN_CITY_TOOL = {
    "type": "function",
    "function": {
        "name": "find_stations_in_city",
        "description": (
            "List the EV charging stations in one named city, with operator, "
            "connector type, power and status. Use this whenever a question "
            "names a specific city."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "One city name, e.g. 'Pune' or 'Bengaluru'.",
                }
            },
            "required": ["city"],
        },
    },
}

CITY_SUMMARY_TOOL = {
    "type": "function",
    "function": {
        "name": "city_summary",
        "description": (
            "Station and connector counts for EVERY city, with average power. "
            "Use this for comparisons across cities, or questions like which "
            "city has the most or fewest stations. Takes no arguments."
        ),
        # No parameters — but the key must still be present and well-formed.
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}

FAST_CHARGERS_TOOL = {
    "type": "function",
    "function": {
        "name": "find_fast_chargers",
        "description": (
            "In-service stations at or above a given power in kW, across all "
            "cities. Use this for questions about fast charging, high-power "
            "sites, or 'where can I charge quickly'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "min_power_kw": {
                    "type": "number",
                    "description": "Minimum power in kW, e.g. 100.",
                }
            },
            "required": ["min_power_kw"],
        },
    },
}

STATION_TOOLS = {
    "find_stations_in_city": find_stations_in_city,
    "city_summary": city_summary,
    "find_fast_chargers": find_fast_chargers,
}

STATION_MENU = [FIND_IN_CITY_TOOL, CITY_SUMMARY_TOOL, FAST_CHARGERS_TOOL]
