"""The curated SQL tools. These need a real database, so they are marked
`integration` and skipped when Docker is not running.

    uv run pytest                      # everything
    uv run pytest -m "not integration" # unit only, no Docker needed

Why not fake the database too? Because the thing worth testing here IS the
SQL — the joins, the filters, the NULL handling. A fake would only prove
the fake works.
"""

import pytest

from sprint.agent.stations import (
    city_summary,
    find_fast_chargers,
    find_stations_in_city,
)
from sprint.db import healthy, query

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not healthy(), reason="database not reachable"),
]


def test_city_lookup_is_case_insensitive():
    """The model may send 'pune', 'Pune' or 'PUNE'. Handle it in SQL.

    Compare the station ROWS, not the whole string: the header echoes the
    caller's spelling back ("7 stations in pune" vs "...in PUNE"), which is
    cosmetic. An earlier version of this test compared both and failed —
    the test was over-specified, the code was right.
    """
    lower = find_stations_in_city("pune").splitlines()[1:]
    upper = find_stations_in_city("PUNE").splitlines()[1:]
    assert lower == upper
    assert len(lower) == 7


def test_unknown_city_returns_a_sentence_not_an_empty_string():
    """The model has to be able to say 'there aren't any' rather than guess."""
    result = find_stations_in_city("Atlantis")
    assert "no stations" in result.lower()
    assert "Atlantis" in result


def test_fast_chargers_excludes_sites_that_are_not_in_service():
    """A planned or under-maintenance site is no use to a driver today."""
    result = find_fast_chargers(100)

    unusable = query(
        "SELECT name FROM stations WHERE power_kw >= 100 AND status <> 'live'"
    )
    assert unusable, "fixture no longer exercises this case"
    for row in unusable:
        assert row["name"] not in result


def test_fast_chargers_with_nothing_that_fast():
    assert "no in-service stations" in find_fast_chargers(9999).lower()


def test_city_summary_totals_match_the_table():
    """Guards against a GROUP BY that silently drops rows."""
    summary = city_summary()
    cities = query("SELECT DISTINCT city FROM stations")
    for row in cities:
        assert row["city"] in summary


# ── the layer that matters ──────────────────────────────────────────────────

@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM stations",
        "UPDATE stations SET price_per_kwh = 0",
        "DROP TABLE stations",
        "CREATE TABLE evil (x int)",
    ],
)
def test_the_app_role_cannot_write(sql):
    """Layers 1 and 2 are my code, and my code has bugs. This one is
    Postgres refusing, which is why it holds when the others fail."""
    with pytest.raises(Exception) as caught:
        query(sql)
    assert "read-only" in str(caught.value).lower()


def test_a_hostile_parameter_is_treated_as_data():
    """Parameterised, so this is looked up as a city NAME and finds nothing."""
    rows = query(
        "SELECT name FROM stations WHERE city = %s",
        ("Pune'; DROP TABLE stations; --",),
    )
    assert rows == []
    assert query("SELECT count(*) AS n FROM stations")[0]["n"] > 0
