"""Dome observatory control. Endpoints confirmed against ninaAPI source at
WebService/V2/Equipment/Dome.cs. Connect the dome first via
`nina_connect_device(device="dome")`.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..nina_client import client


async def nina_dome_info() -> dict:
    """Get dome status: connection state, shutter state, azimuth angle,
    slewing state, parked state, and dome-follows-mount status.
    """
    return await client.get("/equipment/dome/info")


async def nina_dome_open() -> dict:
    """Open the dome shutter."""
    return await client.get("/equipment/dome/open")


async def nina_dome_close() -> dict:
    """Close the dome shutter."""
    return await client.get("/equipment/dome/close")


async def nina_dome_slew(azimuth: float) -> dict:
    """Slew the dome to a specific azimuth angle.

    azimuth: Target azimuth in degrees (0.0 to 360.0). North is 0.0, East is 90.0.
    """
    if not (0.0 <= azimuth <= 360.0):
        raise ValueError(f"azimuth must be between 0.0 and 360.0 degrees, got {azimuth}")
    return await client.get("/equipment/dome/slew", azimuth=azimuth)


def register(mcp: FastMCP) -> None:
    mcp.tool()(nina_dome_info)
    mcp.tool()(nina_dome_open)
    mcp.tool()(nina_dome_close)
    mcp.tool()(nina_dome_slew)
