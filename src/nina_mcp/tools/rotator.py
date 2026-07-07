"""Rotator control. Endpoints confirmed against ninaAPI source at
WebService/V2/Equipment/Rotator.cs. Connect the rotator first via
`nina_connect_device(device="rotator")`.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..nina_client import client


async def nina_rotator_info() -> dict:
    """Get rotator status: connection state, current sky and mechanical position
    angles in degrees, moving state, and direction settings.
    """
    return await client.get("/equipment/rotator/info")


async def nina_rotator_move(angle: float) -> dict:
    """Slew the rotator to a specific sky angle.

    angle: Target sky position angle in degrees (0.0 to 360.0).
    """
    if not (0.0 <= angle <= 360.0):
        raise ValueError(f"angle must be between 0.0 and 360.0 degrees, got {angle}")
    return await client.get("/equipment/rotator/move", angle=angle)


async def nina_rotator_stop() -> dict:
    """Stop any in-progress rotator movement."""
    return await client.get("/equipment/rotator/stop-move")


def register(mcp: FastMCP) -> None:
    mcp.tool()(nina_rotator_info)
    mcp.tool()(nina_rotator_move)
    mcp.tool()(nina_rotator_stop)
