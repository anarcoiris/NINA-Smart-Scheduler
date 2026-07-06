"""Safe, generic read/write access to Target Scheduler's SQLite database.

Why this exists instead of REST calls: the ninaAPI ("Advanced API") plugin
does NOT expose endpoints for Target Scheduler's project/target/exposure-plan
data. It only forwards a couple of read-only status events (see
tools/target_scheduler.py's docstring for the full explanation). The plugin's
own documentation confirms all of that data lives in a SQLite database at
`%LOCALAPPDATA%\\NINA\\SchedulerPlugin\\schedulerdb.sqlite`
(https://tcpalmer.github.io/nina-scheduler/technical-details.html).

Rather than hardcode table/column names I haven't verified against a live
database (TS's schema has changed across major versions -- e.g. the TS5
migration), this module works generically: discover tables and columns at
call time via SQLite's own metadata, and validate every identifier against
that before building SQL. Values are always parameterized. Writes are
gated behind `settings.ts_allow_writes` and restricted to a single-row,
single-column UPDATE by id -- there's no facility here for arbitrary DELETE,
DROP, or multi-row writes.

If you want richer TS tools, connect to a copy of your live schedulerdb.sqlite
with any SQLite browser first, note down the exact table/column names for
your installed TS version, and add typed wrapper tools on top of the
generic ones below.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any, Optional

from .config import settings

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class TargetSchedulerDBError(Exception):
    pass


def _quote_ident(name: str) -> str:
    if not _IDENTIFIER_RE.match(name):
        raise TargetSchedulerDBError(f"Not a valid SQL identifier: {name!r}")
    return f'"{name}"'


def _connect(readonly: bool = True) -> sqlite3.Connection:
    db_path = Path(settings.ts_db_path)
    if not db_path.exists():
        raise TargetSchedulerDBError(
            f"Target Scheduler database not found at {db_path}. Set TS_DB_PATH "
            f"if this server isn't running on the same PC as NINA, or if TS "
            f"data lives somewhere non-default."
        )
    uri = f"file:{db_path.as_posix()}?mode={'ro' if readonly else 'rw'}"
    try:
        return sqlite3.connect(uri, uri=True)
    except sqlite3.Error as e:
        raise TargetSchedulerDBError(f"Could not open Target Scheduler database: {e}") from e


def list_tables() -> list[str]:
    with _connect(readonly=True) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        ).fetchall()
        return [r[0] for r in rows]


def describe_table(table: str) -> list[dict[str, Any]]:
    _validate_table(table)
    with _connect(readonly=True) as conn:
        cols = conn.execute(f"PRAGMA table_info({_quote_ident(table)})").fetchall()
        return [
            {"cid": c[0], "name": c[1], "type": c[2], "notnull": bool(c[3]), "pk": bool(c[5])}
            for c in cols
        ]


def _validate_table(table: str) -> None:
    if table not in list_tables():
        raise TargetSchedulerDBError(f"Unknown table {table!r}. Call ts_list_tables first.")


def _validate_columns(table: str, columns: list[str]) -> None:
    known = {c["name"] for c in describe_table(table)}
    unknown = [c for c in columns if c not in known]
    if unknown:
        raise TargetSchedulerDBError(
            f"Unknown column(s) {unknown} in table {table!r}. Known columns: {sorted(known)}"
        )


def read_table(
    table: str,
    where_column: Optional[str] = None,
    where_value: Optional[Any] = None,
    limit: int = 200,
) -> list[dict[str, Any]]:
    _validate_table(table)
    limit = max(1, min(int(limit), 2000))
    sql = f"SELECT * FROM {_quote_ident(table)}"
    params: tuple = ()
    if where_column is not None:
        _validate_columns(table, [where_column])
        sql += f" WHERE {_quote_ident(where_column)} = ?"
        params = (where_value,)
    sql += f" LIMIT {limit}"
    with _connect(readonly=True) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def update_cell(
    table: str,
    id_column: str,
    id_value: Any,
    column: str,
    value: Any,
) -> int:
    """Update a single column for a single row, identified by id_column=id_value.
    Returns the number of rows affected (0 or 1 in normal use). Refuses to run
    unless TS_ALLOW_WRITES is set truthy in the environment.
    """
    if not settings.ts_allow_writes:
        raise TargetSchedulerDBError(
            "Writes to the Target Scheduler database are disabled. Set "
            "TS_ALLOW_WRITES=true in the environment once you've confirmed "
            "this is what you want -- ideally after backing up schedulerdb.sqlite."
        )
    _validate_table(table)
    _validate_columns(table, [id_column, column])
    sql = (
        f"UPDATE {_quote_ident(table)} SET {_quote_ident(column)} = ? "
        f"WHERE {_quote_ident(id_column)} = ?"
    )
    with _connect(readonly=False) as conn:
        cur = conn.execute(sql, (value, id_value))
        conn.commit()
        return cur.rowcount
