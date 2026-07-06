# nina-mcp

An MCP server that gives an AI agent (your openclaw agent, Claude, or anything
else that speaks MCP) control over **N.I.N.A.** (Nighttime Imaging 'N'
Astronomy) — mount, camera, and the Advanced Sequencer are fully implemented;
Target Scheduler is covered too, with an important caveat explained below;
everything else (filter wheel, focuser, rotator, dome, guider, safety
monitor, weather, switch, flat device) has working status reads and clearly
marked placeholders for control actions.

It talks to NINA over HTTP via the community **[ninaAPI]** plugin (also
called "Advanced API" in the NINA plugin list) — this MCP server doesn't
replace that plugin, it wraps it.

[ninaAPI]: https://github.com/christian-photo/ninaAPI

## Prerequisites

1. NINA installed and running, with the **Advanced API** plugin installed
   (NINA > Plugins > search "Advanced API") and enabled.
2. Note the host/port it's listening on (NINA > Options > Plugins > Advanced
   API — default port is `1888`). If this MCP server runs on the same PC as
   NINA, the default `127.0.0.1:1888` just works.
3. Python 3.10+ wherever this MCP server runs.

## Install

```bash
cd nina-mcp
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -e .
```

Copy `.env.example` to `.env` and adjust `NINA_HOST` / `NINA_PORT` if needed
(defaults assume NINA is on the same machine, default port).

## Run it

Directly, for any MCP client that spawns servers over stdio (Claude Desktop,
Claude Code, and presumably your openclaw agent — MCP's stdio transport is
just "run this command, talk JSON-RPC over its stdin/stdout"):

```bash
nina-mcp
# or: python -m nina_mcp.server
```

Point your MCP client's config at it. The generic shape (adjust keys to
whatever openclaw's config format expects — this is the same shape Claude
Desktop uses):

```json
{
  "mcpServers": {
    "nina": {
      "command": "/absolute/path/to/nina-mcp/.venv/bin/python",
      "args": ["-m", "nina_mcp.server"],
      "env": {
        "NINA_HOST": "127.0.0.1",
        "NINA_PORT": "1888"
      }
    }
  }
}
```

If openclaw needs a network transport instead of stdio (SSE / streamable
HTTP), FastMCP supports that too — change the `mcp.run()` call in
`server.py` to `mcp.run(transport="streamable-http")` (see the `mcp` Python
SDK docs for the current options; this changed a couple of times across
versions).

### Testing without an agent

`test_client.py` is a minimal MCP client included so you can sanity-check the
server without wiring up openclaw first. It spawns the server itself over
stdio, same as a real client would:

```bash
python test_client.py                                  # list all tools
python test_client.py nina_mount_info                   # call with no args
python test_client.py nina_mount_sync ra=10.5 dec=41.2   # call with args
```

## What's actually implemented

### Core (full control)

- **Equipment (generic, `tools/equipment.py`)** — combined status, list
  available devices, connect/disconnect/rescan any device by name, and
  poll recent event history. Connect equipment through these tools before
  using the device-specific ones below.
- **Mount (`tools/mount.py`)** — info, home, park/unpark, tracking mode,
  slew (raw, center, or center+rotate), stop slew, sync, meridian flip, set
  park position.
- **Camera (`tools/camera.py`)** — info, capture (all the knobs: duration,
  gain, save, target name, image type, plate-solve, binning, readout mode),
  abort exposure, capture statistics, cooling/warming, dew heater, USB
  limit.
- **Sequencer (`tools/sequencer.py`)** — get sequence JSON/state, start,
  stop, reset, skip, edit a field in place, list/load saved sequences by
  name, load a full sequence from JSON, update a target's coordinates.

### Target Scheduler — read this before assuming "full control"

**ninaAPI does not expose Target Scheduler's projects/targets/exposure plans
as REST endpoints.** I checked ninaAPI's source directly
(`WebService/V2/Application/TargetScheduler.cs`): all it does is forward
three of TS's internal status messages (wait-start, new-target-start,
target-start) as read-only events. There's no endpoint to list projects,
change priorities, or ask what it'll image next — that logic is entirely
internal to the Target Scheduler plugin's own Planning Engine, which only
runs from inside a NINA sequence via its "Target Scheduler Container"
instruction (which you still have to build once, by hand, in the NINA UI —
no API creates it for you either).

So `tools/target_scheduler.py` gives you the two things that actually exist:

1. **Running it** — just a normal sequence. Build a sequence containing a
   Target Scheduler Container instruction in NINA's UI once, then use
   `nina_sequence_load_by_name` + `nina_sequence_start` to run it.
2. **Reading/editing its data** — Target Scheduler stores everything in a
   local SQLite database (`schedulerdb.sqlite`, path documented in the
   plugin's own docs). Rather than hardcode column names I couldn't verify
   against a real database (the schema changed across major TS versions),
   `ts_db.py` implements generic, schema-validated tools: `ts_list_tables`,
   `ts_describe_table`, `ts_read_table`, and a narrow `ts_update_cell`
   (single column, single row, by id) that's **disabled by default** —
   set `TS_ALLOW_WRITES=true` once you've backed up your database and want
   an agent editing it. `ts_recent_events` polls the live status events
   from (1).

If you want richer, typed TS tools (e.g. `ts_set_project_priority`), open
your real `schedulerdb.sqlite` in any SQLite browser, confirm the exact
table/column names for your installed TS version, and add typed wrappers on
top of the generic ones — same pattern as `mount.py`/`camera.py`.

### Placeholders (`tools/placeholders.py`)

Filter wheel, focuser, rotator, dome, guider, safety monitor, weather,
switch, and flat device each get a working `*_info` status read (cheap,
already verified against ninaAPI's source). Their action tools
(`nina_focuser_move`, `nina_dome_open`, etc.) are stubs that raise a clear
error naming the exact, verified REST endpoint and query parameters to wire
up — same pattern as the core modules, just not built out yet.

## Architecture

```
src/nina_mcp/
  config.py           settings from environment variables
  nina_client.py       async HTTP client, unwraps ninaAPI's response envelope
  ts_db.py              generic, schema-validated SQLite access for Target Scheduler
  server.py             FastMCP app, registers every tool module
  tools/
    equipment.py         generic connect/disconnect/list/rescan/event-history
    mount.py             full mount control
    camera.py            full camera control
    sequencer.py         full sequencer control
    target_scheduler.py  DB + event-based TS tools (see caveat above)
    placeholders.py       status reads + stubs for everything else
test_client.py          minimal standalone MCP client for manual testing
```

Every endpoint path and query parameter here was confirmed against ninaAPI's
own C# source (`WebService/V2/...`), not guessed from third-party docs —
I pulled the repo and grepped the `[Route(...)]` attributes directly. The one
thing that genuinely doesn't exist upstream is Target Scheduler's REST API,
which is why that module takes a different approach.

## Safety notes

- This gives an agent real control of a telescope mount and camera. A
  clumsy `nina_mount_slew` or an unattended `nina_sequence_start` can point
  expensive optics somewhere bad or burn a night's imaging. Consider keeping
  a human in the loop for anything that moves hardware until you trust the
  setup.
- `TS_ALLOW_WRITES` is off by default for a reason — back up
  `schedulerdb.sqlite` before turning it on.
- `nina_camera_capture`'s `omit_image` defaults to `True` to avoid dumping
  large base64 blobs into an agent's context by default.
