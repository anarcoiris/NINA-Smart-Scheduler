"""Focuser control. Endpoints confirmed against ninaAPI source at
WebService/V2/Equipment/Focuser.cs. Connect the focuser first via
`nina_connect_device(device="focuser")`.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..nina_client import client


async def nina_focuser_info() -> dict:
    """Get focuser status: connection state, current step position,
    ambient temperature, moving state, and temperature compensation state.
    """
    return await client.get("/equipment/focuser/info")


async def nina_focuser_move(position: int) -> dict:
    """Move the focuser to a specific absolute step position.

    position: Target absolute position in steps. Must be >= 0.
    """
    if position < 0:
        raise ValueError(f"position must be a non-negative integer, got {position}")
    return await client.get("/equipment/focuser/move", position=position)


async def nina_focuser_stop() -> dict:
    """Immediately stop any in-progress focuser movement."""
    return await client.get("/equipment/focuser/stop-move")


def register(mcp: FastMCP) -> None:
    mcp.tool()(nina_focuser_info)
    mcp.tool()(nina_focuser_move)
    mcp.tool()(nina_focuser_stop)
