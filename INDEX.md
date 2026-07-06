# Index

A single lookup point for every doc, topic, source file, and tool in this
project. If you know roughly what you're looking for, find it here rather
than reading README.md and CONTRIBUTING.md end to end.

## Documents

| Doc | What it's for |
|---|---|
| [README.md](README.md) | Overview, prerequisites, install, run, safety notes |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Architecture, hard invariants, how to extend or request a change |
| INDEX.md (this file) | Cross-reference: topic → doc section → source file |
| [docs/research/placeholder_endpoints.md](docs/research/placeholder_endpoints.md) | Research plans for placeholders & TS DB schema |
| [docs/api/proposed_endpoints.md](docs/api/proposed_endpoints.md) | Proposed API signatures for placeholder promotions |
| [docs/tasks/implementation_plan.md](docs/tasks/implementation_plan.md) | Implementation milestones, roadmap, and tasks |


## Topic index

| Topic | Where |
|---|---|
| Architecture / module layout | [CONTRIBUTING § Architecture](CONTRIBUTING.md#architecture) |
| Camera capture (params, defaults) | [tools/camera.py](src/nina_mcp/tools/camera.py) `nina_camera_capture`; see [Tool reference § Camera](#camera-toolscamerapy) |
| Config / environment variables | [README § Install](README.md#install); [Environment variables](#environment-variables) below; [src/nina_mcp/config.py](src/nina_mcp/config.py) |
| Connecting equipment (generic pattern) | [Tool reference § Equipment](#equipment-generic-toolsequipmentpy); [CONTRIBUTING § Generic device lifecycle](CONTRIBUTING.md#design-patterns-in-use) |
| Contributing / extending the code | [CONTRIBUTING.md](CONTRIBUTING.md) (entire doc) |
| Design patterns (envelope unwrapping, generic SQL, placeholders) | [CONTRIBUTING § Design patterns in use](CONTRIBUTING.md#design-patterns-in-use) |
| Event history / polling for status | [tools/equipment.py](src/nina_mcp/tools/equipment.py) `nina_get_event_history`; [tools/target_scheduler.py](src/nina_mcp/tools/target_scheduler.py) `ts_recent_events` |
| Extending a placeholder | [CONTRIBUTING § Extending a placeholder](CONTRIBUTING.md#extending-a-placeholder-into-a-full-implementation) |
| Invariants (hard rules) | [CONTRIBUTING § Invariants](CONTRIBUTING.md#invariants-things-this-codebase-never-does) |
| MCP client config (openclaw, Claude Desktop, etc.) | [README § Run it](README.md#run-it) |
| Mount slew (RA in hours, not degrees) | [tools/mount.py](src/nina_mcp/tools/mount.py) `nina_mount_slew` |
| Placeholder pattern | [CONTRIBUTING § Design patterns in use](CONTRIBUTING.md#design-patterns-in-use); [tools/placeholders.py](src/nina_mcp/tools/placeholders.py) |
| Requesting a change / filing a bug | [CONTRIBUTING § Requesting a change](CONTRIBUTING.md#requesting-a-change) |
| Response envelope (`Success`/`Error`/`Response`) | [src/nina_mcp/nina_client.py](src/nina_mcp/nina_client.py); [CONTRIBUTING § Design patterns in use](CONTRIBUTING.md#design-patterns-in-use) |
| Safety notes | [README § Safety notes](README.md#safety-notes) |
| Sequencer / Advanced Sequencer control | [Tool reference § Sequencer](#sequencer-toolssequencerpy) |
| SQL injection protection (Target Scheduler DB) | [src/nina_mcp/ts_db.py](src/nina_mcp/ts_db.py) `_validate_table`/`_validate_columns`; [CONTRIBUTING § Invariants, #2](CONTRIBUTING.md#invariants-things-this-codebase-never-does) |
| Target Scheduler | [README § What's implemented](README.md#whats-implemented); [tools/target_scheduler.py](src/nina_mcp/tools/target_scheduler.py) module docstring (full explanation of why there's no REST control surface) |
| Testing approach | [CONTRIBUTING § Testing](CONTRIBUTING.md#testing) |
| Test client (manual tool calls without an agent) | [README § Testing without an agent](README.md#testing-without-an-agent); [test_client.py](test_client.py) |
| Transports (stdio vs HTTP/SSE) | [Transports](#transports) below |
| `TS_ALLOW_WRITES` | [.env.example](.env.example); [CONTRIBUTING § Invariants, #3](CONTRIBUTING.md#invariants-things-this-codebase-never-does) |
| Where the endpoint facts came from | [CONTRIBUTING § Where the facts came from](CONTRIBUTING.md#where-the-facts-came-from) |

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `NINA_HOST` | `127.0.0.1` | Host running NINA + the Advanced API plugin |
| `NINA_PORT` | `1888` | Advanced API plugin's configured port |
| `NINA_API_BASE_PATH` | `/v2/api` | Fixed by the plugin; only change if a future major version ships alongside v2 |
| `NINA_TIMEOUT` | `30` | HTTP request timeout, seconds |
| `TS_DB_PATH` | `%LOCALAPPDATA%\NINA\SchedulerPlugin\schedulerdb.sqlite` | Path to Target Scheduler's SQLite database |
| `TS_ALLOW_WRITES` | `false` | Must be explicitly set truthy to enable `ts_update_cell` |

Defined in [src/nina_mcp/config.py](src/nina_mcp/config.py); template in
[.env.example](.env.example).

## Transports

Default is stdio (`mcp.run()` in `server.py`), which is what Claude
Desktop/Code and most local MCP clients expect — the client spawns this
server as a subprocess and talks JSON-RPC over its stdin/stdout. If your
agent needs a network transport instead, change that call to
`mcp.run(transport="streamable-http")` (check the installed `mcp` SDK
version's docs for exact supported transport names, as this has changed
across SDK versions).

## Tool reference

Every registered tool, grouped by module. One line each — full parameter
docs live in each tool's own docstring in the source file linked in the
section header.

### Equipment, generic (`tools/equipment.py`)

| Tool | Does |
|---|---|
| `nina_get_all_equipment_info` | Combined status snapshot of every equipment category |
| `nina_list_devices` | List available devices for a category (returns Ids for `nina_connect_device`) |
| `nina_connect_device` | Connect a device by category, optionally a specific Id |
| `nina_disconnect_device` | Disconnect a device |
| `nina_rescan_devices` | Re-scan for available devices in a category |
| `nina_get_event_history` | Recent event/notification history (also used for Target Scheduler polling) |

### Mount (`tools/mount.py`)

| Tool | Does |
|---|---|
| `nina_mount_info` | Full mount status |
| `nina_mount_home` | Send mount to home position |
| `nina_mount_park` | Park the mount |
| `nina_mount_unpark` | Unpark the mount |
| `nina_mount_set_tracking_mode` | Set tracking rate: sidereal/lunar/solar/king/stopped |
| `nina_mount_slew` | Slew to J2000 RA (hours)/Dec (degrees), optional center/rotate |
| `nina_mount_stop_slew` | Stop an in-progress slew |
| `nina_mount_sync` | Sync mount's position without moving it |
| `nina_mount_meridian_flip` | Perform a meridian flip |
| `nina_mount_set_park_position` | Set current position as park position |

### Camera (`tools/camera.py`)

| Tool | Does |
|---|---|
| `nina_camera_info` | Full camera status |
| `nina_camera_capture` | Capture an exposure (duration, gain, save, type, solve, and more) |
| `nina_camera_abort_exposure` | Abort the current exposure |
| `nina_camera_capture_statistics` | HFR/star count/ADU stats for the last capture |
| `nina_camera_cool` | Cool to a target temperature |
| `nina_camera_warm` | Warm the camera back up |
| `nina_camera_set_binning` | Set binning, e.g. "2x2" |
| `nina_camera_set_readout_mode` | Set readout mode index |
| `nina_camera_set_dew_heater` | Turn the dew heater on/off |
| `nina_camera_set_usb_limit` | Set USB bandwidth limit |

### Sequencer (`tools/sequencer.py`)

| Tool | Does |
|---|---|
| `nina_sequence_get_json` | Get the loaded sequence as NINA's JSON structure |
| `nina_sequence_get_state` | Current run state / progress |
| `nina_sequence_start` | Start running the loaded sequence |
| `nina_sequence_stop` | Stop the running sequence |
| `nina_sequence_reset` | Reset sequence to initial state |
| `nina_sequence_skip` | Skip current items / to end / to imaging |
| `nina_sequence_edit` | Edit one field in place by path |
| `nina_sequence_list_available` | List sequence files available to load by name |
| `nina_sequence_load_by_name` | Load a saved sequence by name |
| `nina_sequence_load_json` | Load a full sequence from a raw JSON string |
| `nina_sequence_set_target` | Update a target container's name/coords/rotation |

### Target Scheduler (`tools/target_scheduler.py`)

Read [the module docstring](src/nina_mcp/tools/target_scheduler.py) first —
this is not a REST wrapper like the others.

| Tool | Does |
|---|---|
| `ts_list_tables` | List tables in the Target Scheduler SQLite database |
| `ts_describe_table` | List a table's columns (name, type, nullability, PK) |
| `ts_read_table` | Read rows, optionally filtered by one column=value |
| `ts_update_cell` | Update one column on one row (gated by `TS_ALLOW_WRITES`) |
| `ts_recent_events` | Recent TS-* status events (wait-start, target-start, etc.) forwarded via NINA |

### Placeholders (`tools/placeholders.py`)

Status reads are fully working; action tools raise
`NotImplementedPlaceholder` naming the real endpoint (see
[Extending a placeholder](CONTRIBUTING.md#extending-a-placeholder-into-a-full-implementation)).

| Tool | Status |
|---|---|
| `nina_filterwheel_info` | ✅ working |
| `nina_filterwheel_change_filter` | 🔶 placeholder |
| `nina_focuser_info` | ✅ working |
| `nina_focuser_move` | 🔶 placeholder |
| `nina_rotator_info` | ✅ working |
| `nina_rotator_move` | 🔶 placeholder |
| `nina_dome_info` | ✅ working |
| `nina_dome_open` | 🔶 placeholder |
| `nina_guider_info` | ✅ working |
| `nina_guider_start` | 🔶 placeholder |
| `nina_safetymonitor_info` | ✅ working |
| `nina_weather_info` | ✅ working |
| `nina_switch_info` | ✅ working |
| `nina_switch_set` | 🔶 placeholder |
| `nina_flatdevice_info` | ✅ working |
| `nina_flatdevice_set_light` | 🔶 placeholder |

**Total: 58 tools** — 51 fully working (6 equipment + 10 mount + 10 camera +
11 sequencer + 5 Target Scheduler + 9 placeholder-module status reads), and
7 placeholder stubs awaiting implementation (filter wheel, focuser, rotator,
dome, guider, switch, flat device — one action stub each).
