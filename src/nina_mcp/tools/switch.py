"""Switch control (for relays, power distributions, etc.). Endpoints confirmed
against ninaAPI source at WebService/V2/Equipment/Switch.cs. Connect the switch first
via `nina_connect_device(device="switch")`.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..nina_client import client


async def nina_switch_info() -> dict:
    """Get switch device status: connection and the state/value of each
    configured switch.
    """
    return await client.get("/equipment/switch/info")


async def nina_switch_set(switch_index: int, value: float) -> dict:
    """Set a switch value (e.g. relay state or slider value).

    switch_index: Index of the switch. Must be >= 0.
    value: Target state (0.0 for OFF, 1.0 for ON, or intermediate value for sliders).
    """
    if switch_index < 0:
        raise ValueError(f"switch_index must be a non-negative integer, got {switch_index}")
    return await client.get("/equipment/switch/set", index=switch_index, value=value)


def register(mcp: FastMCP) -> None:
    mcp.tool()(nina_switch_info)
    mcp.tool()(nina_switch_set)
