"""Database access. One pool, one query function, parameterised always.

The connection string points at a READ-ONLY role (sprint_app). That is the
layer that holds when everything above it fails.
"""

from typing import Any

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from .settings import settings

# Never return an unbounded result set — one careless query should not
# drag a million rows into the model's context (and your token bill).
MAX_ROWS = 100

# Built once, reused. Java: a HikariCP DataSource, not a new Connection
# per call. open=False so importing this module doesn't need a live DB.
pool = ConnectionPool(settings.database_url, min_size=1, max_size=5, open=False)


def _ensure_open() -> None:
    """Open the pool on first use.

    open=False above means importing this module never needs a live
    database — tests and linting still work with Docker stopped. The cost
    is that something must open it, and doing that here means the first
    query pays the connection cost instead of every import paying it.
    """
    if pool.closed:
        pool.open(wait=True, timeout=10.0)


def query(sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    """Run a SELECT and return rows as dictionaries.

    `params` are sent separately from `sql` — the driver never splices them
    into the query text. This is a PreparedStatement, and it is why a city
    name like  Pune'; DROP TABLE stations; --  is looked up as a city name
    and finds nothing, rather than being executed.
    """
    _ensure_open()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params)
            return cur.fetchmany(MAX_ROWS)


def healthy() -> bool:
    """Can we reach the database at all?"""
    try:
        return query("SELECT 1 AS ok")[0]["ok"] == 1
    except Exception:
        return False
