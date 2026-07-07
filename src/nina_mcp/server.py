"""NINA MCP server entrypoint.

Run directly for local (stdio) use by an MCP client such as Claude Desktop,
Claude Code, or your openclaw agent:

    python -m nina_mcp.server

Or via the MCP CLI dev tools for interactive testing:

    mcp dev src/nina_mcp/server.py

Configuration is via environment variables -- see config.py and .env.example.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .tools import (
    camera,
    dome,
    equipment,
    filterwheel,
    flatdevice,
    focuser,
    guider,
    mount,
    placeholders,
    rotator,
    sequencer,
    switch,
    target_scheduler,
)

mcp = FastMCP(
    "nina-mcp",
    instructions=(
        "Tools for controlling N.I.N.A. (Nighttime Imaging 'N' Astronomy) astrophotography "
        "software via its Advanced API plugin (ninaAPI). Always check "
        "nina_get_all_equipment_info first to see what's connected. Connect equipment with "
        "nina_connect_device before using device-specific tools. All tools for camera, mount, "
        "sequencer, filter wheel, focuser, rotator, dome, guider, switch, flat device, and "
        "weather/safety monitors are implemented. Target Scheduler has no REST control surface "
        "upstream; ts_* tools read/edit its SQLite database directly and ts_recent_events polls "
        "its status events -- see tools/target_scheduler.py for the full explanation."
    ),
)

# Core & Equipment Modules.
equipment.register(mcp)
mount.register(mcp)
camera.register(mcp)
sequencer.register(mcp)
target_scheduler.register(mcp)
filterwheel.register(mcp)
focuser.register(mcp)
rotator.register(mcp)
dome.register(mcp)
guider.register(mcp)
switch.register(mcp)
flatdevice.register(mcp)

# Status-only placeholders (weather, safety monitor).
placeholders.register(mcp)



def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
