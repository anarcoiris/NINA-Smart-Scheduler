"""Flat panel/flat device control. Endpoints confirmed against ninaAPI source at
WebService/V2/Equipment/FlatDevice.cs. Connect the flat panel first via
`nina_connect_device(device="flatdevice")`.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..nina_client import client


async def nina_flatdevice_info() -> dict:
    """Get flat panel/flat device status: connection, light on/off state,
    brightness, and cover open/closed status.
    """
    return await client.get("/equipment/flatdevice/info")


async def nina_flatdevice_set_light(on: bool) -> dict:
    """Turn the flat panel light on (True) or off (False)."""
    return await client.get("/equipment/flatdevice/set-light", power=on)


def register(mcp: FastMCP) -> None:
    mcp.tool()(nina_flatdevice_info)
    mcp.tool()(nina_flatdevice_set_light)
