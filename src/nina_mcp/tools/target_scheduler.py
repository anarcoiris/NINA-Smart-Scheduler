"""Target Scheduler (tcpalmer's plugin) tools.
"""

from __future__ import annotations

from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .. import ts_db
from ..nina_client import client


async def ts_list_tables() -> list[str]:
    """List every table in the Target Scheduler SQLite database. Start
    here -- table/column names vary across Target Scheduler versions
    (notably the TS5 migration), so don't assume names like "Project" or
    "Target" without checking first.
    """
    return ts_db.list_tables()


async def ts_describe_table(table: str) -> list[dict[str, Any]]:
    """List the columns (name, type, nullability, PK) of a
    Target Scheduler database table, as returned by ts_list_tables.
    """
    return ts_db.describe_table(table)


async def ts_read_table(
    table: str,
    where_column: Optional[str] = None,
    where_value: Optional[Any] = None,
    limit: int = 200,
) -> list[dict[str, Any]]:
    """Read rows from a Target Scheduler database table.

    where_column / where_value: optionally filter to rows where this
        column equals this value.
    limit: max rows to return (capped at 2000).
    """
    return ts_db.read_table(table, where_column, where_value, limit)


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


async def ts_set_project_priority(project_id: int, priority: int) -> dict:
    """Set the scheduling priority for a specific project in the database.

    project_id: The unique ID of the project.
    priority: Target priority integer. Lower values represent higher priority (e.g., 1 is highest).
    """
    # 1. Discover the correct project table name (case-insensitive search)
    tables = ts_db.list_tables()
    project_table = None
    for t in tables:
        if t.lower() in ("project", "projects"):
            project_table = t
            break
    if not project_table:
        raise ValueError(
            "Could not find a project table (expected 'Project' or 'Projects') "
            "in the Target Scheduler database."
        )

    # 2. Inspect columns to find exact casing for ID and Priority columns
    columns = ts_db.describe_table(project_table)
    id_column = None
    priority_column = None
    for col in columns:
        name_lower = col["name"].lower()
        if name_lower == "id":
            id_column = col["name"]
        elif name_lower == "priority":
            priority_column = col["name"]

    if not id_column:
        raise ValueError(f"Could not find an ID column in the '{project_table}' table.")
    if not priority_column:
        raise ValueError(f"Could not find a Priority column in the '{project_table}' table.")

    # 3. Perform the update
    rows_affected = ts_db.update_cell(
        table=project_table,
        id_column=id_column,
        id_value=project_id,
        column=priority_column,
        value=priority,
    )
    return {
        "status": "success",
        "table": project_table,
        "id_column": id_column,
        "priority_column": priority_column,
        "rows_affected": rows_affected,
    }


async def ts_set_project_enabled(project_id: int, enabled: bool) -> dict:
    """Toggle the enabled/active state of a specific project.

    project_id: The unique ID of the project.
    enabled: True to enable/activate the project, False to disable.
    """
    # 1. Discover the correct project table name (case-insensitive search)
    tables = ts_db.list_tables()
    project_table = None
    for t in tables:
        if t.lower() in ("project", "projects"):
            project_table = t
            break
    if not project_table:
        raise ValueError(
            "Could not find a project table (expected 'Project' or 'Projects') "
            "in the Target Scheduler database."
        )

    # 2. Inspect columns to find exact casing for ID and Active/Enabled status columns
    columns = ts_db.describe_table(project_table)
    id_column = None
    enabled_column = None

    state_candidates = {"active", "enabled", "runstate"}
    for col in columns:
        name_lower = col["name"].lower()
        if name_lower == "id":
            id_column = col["name"]
        elif name_lower in state_candidates:
            if not enabled_column or name_lower == "active":
                enabled_column = col["name"]

    if not id_column:
        raise ValueError(f"Could not find an ID column in the '{project_table}' table.")
    if not enabled_column:
        raise ValueError(
            f"Could not find an activation status column (e.g. 'Active', 'Enabled', "
            f"or 'RunState') in the '{project_table}' table."
        )

    # 3. Perform the update
    val = 1 if enabled else 0
    rows_affected = ts_db.update_cell(
        table=project_table,
        id_column=id_column,
        id_value=project_id,
        column=enabled_column,
        value=val,
    )
    return {
        "status": "success",
        "table": project_table,
        "id_column": id_column,
        "enabled_column": enabled_column,
        "rows_affected": rows_affected,
    }


async def ts_toggle_target_enabled(target_id: int, enabled: bool) -> dict:
    """Toggle the enabled/active state of a specific target.

    target_id: The unique ID of the target.
    enabled: True to enable/activate the target, False to disable.
    """
    # 1. Discover the correct target table name (case-insensitive search)
    tables = ts_db.list_tables()
    target_table = None
    for t in tables:
        if t.lower() in ("target", "targets"):
            target_table = t
            break
    if not target_table:
        raise ValueError(
            "Could not find a target table (expected 'Target' or 'Targets') "
            "in the Target Scheduler database."
        )

    # 2. Inspect columns to find exact casing for ID and Active/Enabled/RunState columns
    columns = ts_db.describe_table(target_table)
    id_column = None
    enabled_column = None

    # Common column names representing target activation state
    state_candidates = {"active", "enabled", "runstate"}

    for col in columns:
        name_lower = col["name"].lower()
        if name_lower == "id":
            id_column = col["name"]
        elif name_lower in state_candidates:
            # Prefer 'active' if available, otherwise fallback to whichever matches
            if not enabled_column or name_lower == "active":
                enabled_column = col["name"]

    if not id_column:
        raise ValueError(f"Could not find an ID column in the '{target_table}' table.")
    if not enabled_column:
        raise ValueError(
            f"Could not find an activation status column (e.g. 'Active', 'Enabled', "
            f"or 'RunState') in the '{target_table}' table."
        )

    # 3. Perform the update (using 1 for active/enabled, 0 for inactive/disabled)
    val = 1 if enabled else 0
    rows_affected = ts_db.update_cell(
        table=target_table,
        id_column=id_column,
        id_value=target_id,
        column=enabled_column,
        value=val,
    )
    return {
        "status": "success",
        "table": target_table,
        "id_column": id_column,
        "enabled_column": enabled_column,
        "rows_affected": rows_affected,
    }


async def ts_recent_events(limit: int = 20) -> list[dict]:
    """Get recent Target Scheduler status events forwarded through NINA:
    TS-WAITSTART (scheduler is waiting for the next imaging window),
    TS-NEWTARGETSTART / TS-TARGETSTART (scheduler picked a target and
    started imaging it, with target name, project name, coordinates,
    rotation, and expected end time). This is TS's actual live state --
    the database only holds its configuration and historical progress.
    """
    history = await client.get("/event-history")
    ts_events = [e for e in history if str(e.get("Event", "")).startswith("TS-")]
    return ts_events[-limit:]


def register(mcp: FastMCP) -> None:
    mcp.tool()(ts_list_tables)
    mcp.tool()(ts_describe_table)
    mcp.tool()(ts_read_table)
    mcp.tool()(ts_update_cell)
    mcp.tool()(ts_set_project_priority)
    mcp.tool()(ts_set_project_enabled)
    mcp.tool()(ts_toggle_target_enabled)
    mcp.tool()(ts_recent_events)
