# Contributing to nina-mcp

This project is small enough that "contributing" mostly means: you, or an
AI coding agent (openclaw, Claude Code, whatever) acting on your behalf, are
about to edit this code. This doc is written for either audience. Read
**Invariants** before changing anything — it's the short list of things that
must stay true regardless of what feature you're adding.

## Contents

- [Architecture](#architecture)
- [Invariants: things this codebase never does](#invariants-things-this-codebase-never-does)
- [Extending a placeholder into a full implementation](#extending-a-placeholder-into-a-full-implementation)
- [Adding a new tool from scratch](#adding-a-new-tool-from-scratch)
- [Requesting a change](#requesting-a-change)
- [Testing](#testing)

## Architecture

```
src/nina_mcp/
  config.py             settings from environment variables (Settings dataclass)
  nina_client.py         async HTTP client; unwraps ninaAPI's response envelope
  ts_db.py               generic, schema-validated SQLite access (Target Scheduler)
  server.py              FastMCP app; imports and registers every tool module
  tools/
    equipment.py          generic connect/disconnect/list/rescan/event-history
    mount.py               full mount control
    camera.py              full camera control
    sequencer.py           full sequencer control
    target_scheduler.py    DB- and event-based TS tools
    placeholders.py        status reads + stubs for non-core equipment
test_client.py           minimal standalone MCP client, for manual testing
```

### Design patterns in use

**Central envelope unwrapping.** Every ninaAPI response is
`{Response, Error, StatusCode, Success, Type}`. `NinaClient._unwrap()` in
`nina_client.py` is the *only* place that checks `Success` and raises
`NinaAPIError`. Tool functions just call `client.get(...)` and return
whatever comes back — they never touch `Success`/`Error` themselves. This
means adding a new endpoint is a one-line `client.get("/some/path", **params)`
call, and error handling is already done for you.

**Generic device lifecycle.** `connect`/`disconnect`/`list-devices`/`rescan`
work identically for all eleven device categories, so they're implemented
once in `equipment.py` against a `Literal[...]` of valid device names, rather
than duplicated per device module. Device-specific modules (`mount.py`,
`camera.py`, etc.) assume the device is already connected.

**Schema-validated generic SQL, not hardcoded schema.** `ts_db.py` doesn't
hardcode Target Scheduler's table/column names, because that schema has
changed across TS major versions (notably the TS5 migration) and wasn't
directly verifiable against a live database at the time this was written.
Instead every identifier (table name, column name) is validated against
`PRAGMA table_info` / `sqlite_master` *at call time* before being interpolated
into SQL, and every value is passed as a bound parameter. See
[Invariants](#invariants-things-this-codebase-never-does) for the rule this
implements.

**Placeholder pattern.** Non-core devices get a real `*_info` read (cheap,
verified, low-risk) and a stub for anything that changes state
(`nina_focuser_move`, etc.). Stubs raise `NotImplementedPlaceholder` with the
exact verified endpoint path and params in the message — they never silently
return a fake success. See
[Extending a placeholder](#extending-a-placeholder-into-a-full-implementation).

### Where the facts came from

Every endpoint path, query parameter, and enum value referenced anywhere in
this codebase was confirmed by pulling ninaAPI's own source
(`github.com/christian-photo/ninaAPI`) and grepping its `[Route(...)]`
attributes and `[QueryField]` parameters directly — not copied from
third-party docs or guessed. If you add a new endpoint, hold yourself to the
same standard (see the first invariant below).

## Invariants: things this codebase never does

These are hard rules, not style preferences. A change that violates one of
these should not be merged, no matter how convenient it is in the moment.

1. **Never wire up an endpoint you haven't verified against ninaAPI's actual
   source.** Docs and blog posts go stale; the plugin's own `[Route(...)]`
   attributes don't. If you can't check the source, leave it as a placeholder
   with a note instead of guessing a path or param name.
2. **Never build SQL by string-formatting a table/column name that hasn't
   been validated against `PRAGMA table_info` / `sqlite_master` first.**
   `ts_db.py`'s `_validate_table` / `_validate_columns` exist for exactly
   this. Values always go through parameter binding (`?`), never
   interpolation — no exceptions, even for "trusted" internal callers.
3. **Never flip `TS_ALLOW_WRITES`'s default to `True`.** Writing to a user's
   scheduling database is destructive if something goes wrong, and there's no
   undo. It's opt-in, permanently.
4. **Never make `nina_camera_capture`'s `omit_image` default to `False`.**
   Image payloads are large; defaulting to including them would silently
   blow up an agent's context on every capture.
5. **Never let a placeholder tool silently no-op or return a fake success.**
   If it's not implemented, it must raise, and the error message must name
   the real endpoint so the next person (human or agent) can finish the job
   in minutes, not by re-deriving it from scratch.
6. **Never duplicate `Success`/`Error` envelope-checking logic inside a tool
   function.** That belongs in `NinaClient._unwrap` only. If you find
   yourself checking `response.get("Success")` inside `tools/`, something's
   wrong.
7. **Never add a device-specific connect/disconnect/list/rescan function.**
   That's what the generic `equipment.py` tools are for. A new device
   category gets added to the `DeviceName` literal there, not a bespoke
   `nina_<device>_connect` tool.
8. **Never add a runtime dependency without a strong reason.** This project
   intentionally has exactly two: `mcp` and `httpx`. Adding an ORM, a second
   HTTP client, or a settings-management library for convenience is not a
   strong reason.

## Extending a placeholder into a full implementation

`tools/placeholders.py` documents the real endpoint for every stub. To
promote one:

1. Read the stub's docstring for the endpoint path and any known params.
2. Re-verify against ninaAPI's source if you have any doubt (see invariant
   1) — pull the repo, grep the relevant file under `WebService/V2/Equipment/`.
3. Replace the `raise NotImplementedPlaceholder(...)` body with a
   `return await client.get(path, **params)` call, following the exact style
   of `mount.py` or `camera.py` (type-hinted params, a docstring explaining
   units/ranges/defaults).
4. If the device category doesn't have its own module yet and you're adding
   several tools for it, consider giving it one (`tools/focuser.py`, etc.)
   rather than growing `placeholders.py` indefinitely — but a single tool
   can stay there.
5. Register nothing extra in `server.py` — `placeholders.register(mcp)` and
   friends already pick up whatever's defined in the module.
6. Add it to [INDEX.md](INDEX.md)'s topic index.

## Adding a new tool from scratch

Same shape every time:

```python
@mcp.tool()
async def nina_<device>_<action>(param: type, optional_param: type = default) -> dict:
    """One-line summary.

    Longer explanation of units, ranges, and side effects if any parameter
    isn't self-explanatory (see mount.py's nina_mount_slew for a good example
    of documenting units explicitly -- RA in hours, not degrees, has bitten
    people).
    """
    return await client.get("/verified/endpoint/path", queryParam=param, ...)
```

Notes:
- `client.get`/`client.post_raw_body` drop `None`-valued params automatically
  — pass `Optional[...] = None` for anything genuinely optional.
- Validate enum-like string inputs yourself before calling out (see
  `nina_mount_set_tracking_mode`'s `TRACKING_MODES` dict) rather than letting
  NINA reject an invalid value with a less helpful error.
- Tool docstrings are what an agent sees when deciding whether/how to call a
  tool — write them for that audience, not just as internal comments.

## Requesting a change

Whether you're filing this for a human or handing it to an agent, include:

- **What NINA/ninaAPI capability you want.** Link the exact source file/line
  in `christian-photo/ninaAPI` if you've already found it, or describe the
  NINA UI feature if you haven't looked yet.
- **Which tool(s) it affects** — a new one, or a change to an existing
  signature (which is a breaking change for anything already calling it).
- **Whether it's read-only or state-changing.** State-changing tools on
  mount/camera/sequencer/Target-Scheduler-writes get extra scrutiny per the
  [Invariants](#invariants-things-this-codebase-never-does) above.

Bug reports should include the failing tool name, the arguments passed, and
the raw error text (`NinaAPIError` messages already include NINA's own
`Error` field, which is usually the useful part).

## Testing

There's no live NINA instance in CI, so tests mock at two levels:

- **HTTP layer:** swap `nina_client.client._client` for an
  `httpx.AsyncClient(transport=httpx.MockTransport(handler))` and assert on
  request params / return crafted envelope responses. This exercises the
  real tool functions and the real envelope-unwrapping logic with zero actual
  network I/O.
- **Target Scheduler DB:** point `TS_DB_PATH` at a throwaway SQLite file you
  create with the tables/columns you want to test against, rather than a
  real `schedulerdb.sqlite`.

Both patterns are demonstrated in full in this project's development history
— search for `httpx.MockTransport` and `sqlite3.connect` usage if you need a
template. When adding a new tool, add at least one success case and one
failure-envelope case (`"Success": false`).
