"""Guider (autoguiding) control. Endpoints confirmed against ninaAPI source at
WebService/V2/Equipment/Guider.cs. Connect the guider first via
`nina_connect_device(device="guider")`.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..nina_client import client


async def nina_guider_info() -> dict:
    """Get autoguider status: connection state, guiding state, and last guide
    step/RMS error info.
    """
    return await client.get("/equipment/guider/info")


async def nina_guider_start(calibrate: bool = False) -> dict:
    """Start the autoguider loop.

    calibrate: True to force a new calibration sequence, False to use existing calibration.
    """
    return await client.get("/equipment/guider/start", calibrate=calibrate)


async def nina_guider_stop() -> dict:
    """Stop autoguiding."""
    return await client.get("/equipment/guider/stop")


def register(mcp: FastMCP) -> None:
    mcp.tool()(nina_guider_info)
    mcp.tool()(nina_guider_start)
    mcp.tool()(nina_guider_stop)
