"""Filter wheel control. Endpoints confirmed against ninaAPI source at
WebService/V2/Equipment/FilterWheel.cs. Connect the filter wheel first via
`nina_connect_device(device="filterwheel")`.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..nina_client import client


async def nina_filterwheel_info() -> dict:
    """Get filter wheel status: connection state, current filter index,
    list of available filters, and their focus offsets.
    """
    return await client.get("/equipment/filterwheel/info")


async def nina_filterwheel_change_filter(filter_id: int) -> dict:
    """Change the active filter in the filter wheel.

    filter_id: The index/position of the filter to change to (0-indexed). Must be >= 0.
    """
    if filter_id < 0:
        raise ValueError(f"filter_id must be a non-negative integer, got {filter_id}")
    return await client.get("/equipment/filterwheel/change-filter", filter=filter_id)


def register(mcp: FastMCP) -> None:
    mcp.tool()(nina_filterwheel_info)
    mcp.tool()(nina_filterwheel_change_filter)
