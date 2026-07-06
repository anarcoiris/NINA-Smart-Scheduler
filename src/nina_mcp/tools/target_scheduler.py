"""Target Scheduler (tcpalmer's plugin) tools.

IMPORTANT, please read before wiring an agent up to "control" Target Scheduler:

ninaAPI (the Advanced API plugin these other tool modules talk to over REST)
does NOT expose Target Scheduler's projects/targets/exposure plans as REST
endpoints. Looking at ninaAPI's own source
(WebService/V2/Application/TargetScheduler.cs), all it does is subscribe to
three of TS's internal pub/sub messages (TargetScheduler-WaitStart,
-NewTargetStart, -TargetStart) and forward them as read-only websocket/event
history entries prefixed "TS-". There is no endpoint to list projects, change
priorities, enable/disable targets, or ask "what will you image next" -- that
logic lives entirely inside Target Scheduler's own Planning Engine, invoked
only from within a running NINA sequence via its "Target Scheduler Container"
instruction.

So "controlling" Target Scheduler from here means two different things:

1. RUNNING it: exactly like any other sequence. Build a sequence in the NINA
   UI containing a Target Scheduler Container instruction (one time, by hand
   -- ninaAPI can't create this instruction for you either), then use the
   sequencer tools (nina_sequence_load_by_name + nina_sequence_start) to run
   it. TS then autonomously picks targets for the rest of that session.

2. READING/EDITING its data: TS stores everything in a local SQLite database
   (see ts_db.py for why we go this route and its safety constraints). The
   generic tools below let an agent inspect that database, and -- only if you
   explicitly opt in via TS_ALLOW_WRITES -- make narrow single-cell edits
   (e.g. flipping a project or target's "enabled" flag, or nudging a
   priority). This is the same thing a human would otherwise do by opening
   schedulerdb.sqlite in a SQLite browser.

Watching what TS actually does mid-session is covered by
`nina_get_event_history` in equipment.py (filter for "Event" values starting
with "TS-").
"""

from __future__ import annotations

from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .. import ts_db
from ..nina_client import client


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def ts_list_tables() -> list[str]:
        """List every table in the Target Scheduler SQLite database. Start
        here -- table/column names vary across Target Scheduler versions
        (notably the TS5 migration), so don't assume names like "Project" or
        "Target" without checking first."""
        return ts_db.list_tables()

    @mcp.tool()
    async def ts_describe_table(table: str) -> list[dict[str, Any]]:
        """List the columns (name, type, nullability, primary key) of a
        Target Scheduler database table, as returned by ts_list_tables."""
        return ts_db.describe_table(table)

    @mcp.tool()
    async def ts_read_table(
        table: str,
        where_column: Optional[str] = None,
        where_value: Optional[Any] = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        """Read rows from a Target Scheduler database table (e.g. projects,
        targets, or exposure plans -- use ts_list_tables/ts_describe_table to
        find the right names for your TS version).

        where_column / where_value: optionally filter to rows where this
            column equals this value (e.g. a project's Id, to find its
            targets via a foreign key column).
        limit: max rows to return (capped at 2000).
        """
        return ts_db.read_table(table, where_column, where_value, limit)

    @mcp.tool()
    async def ts_update_cell(
        table: str, id_column: str, id_value: Any, column: str, value: Any
    ) -> dict:
        """Update a single column on a single row in the Target Scheduler
        database, e.g. disabling a target or bumping a project's priority.

        Disabled by default for safety -- set the environment variable
        TS_ALLOW_WRITES=true to enable this tool, ideally after backing up
        schedulerdb.sqlite. Only ever touches one column on one row
        (identified by id_column=id_value); there's no bulk-edit or delete
        here on purpose.
        """
        rows_affected = ts_db.update_cell(table, id_column, id_value, column, value)
        return {"rows_affected": rows_affected}

    @mcp.tool()
    async def ts_recent_events(limit: int = 20) -> list[dict]:
        """Get recent Target Scheduler status events forwarded through NINA:
        TS-WAITSTART (scheduler is waiting for the next imaging window),
        TS-NEWTARGETSTART / TS-TARGETSTART (scheduler picked a target and
        started imaging it, with target name, project name, coordinates,
        rotation, and expected end time). This is TS's actual live state --
        the database only holds its configuration and historical progress."""
        history = await client.get("/event-history")
        ts_events = [e for e in history if str(e.get("Event", "")).startswith("TS-")]
        return ts_events[-limit:]
