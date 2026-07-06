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

from .tools import camera, equipment, mount, placeholders, sequencer, target_scheduler

mcp = FastMCP(
    "nina-mcp",
    instructions=(
        "Tools for controlling N.I.N.A. (Nighttime Imaging 'N' Astronomy) astrophotography "
        "software via its Advanced API plugin (ninaAPI). Always check "
        "nina_get_all_equipment_info first to see what's connected. Connect equipment with "
        "nina_connect_device before using device-specific tools. Mount, camera, and sequencer "
        "tools are fully implemented; filter wheel/focuser/rotator/dome/guider/safety "
        "monitor/weather/switch/flat-device have working status reads but their action tools "
        "are placeholders -- calling one raises a clear error naming the real endpoint to wire "
        "up. Target Scheduler has no REST control surface upstream; ts_* tools read/edit its "
        "SQLite database directly and ts_recent_events polls its status events -- see "
        "tools/target_scheduler.py for the full explanation."
    ),
)

# Core, fully implemented.
equipment.register(mcp)
mount.register(mcp)
camera.register(mcp)
sequencer.register(mcp)
target_scheduler.register(mcp)

# Non-core: status reads work, action tools are placeholders.
placeholders.register(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
