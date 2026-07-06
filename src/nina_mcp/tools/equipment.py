"""Generic, device-agnostic equipment management.

These four endpoints work identically for every device ninaAPI knows about,
so they're implemented once instead of once-per-device. Every other module
(mount, camera, and the placeholders) assumes its device is already connected
via these tools.

Valid `device` values (confirmed from ninaAPI source, WebService/V2/Equipment/
Connection.cs): camera, dome, filterwheel, flatdevice, focuser, guider,
mount, rotator, safetymonitor, switch, weather.
"""

from __future__ import annotations

from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP

from ..nina_client import client

DeviceName = Literal[
    "camera",
    "dome",
    "filterwheel",
    "flatdevice",
    "focuser",
    "guider",
    "mount",
    "rotator",
    "safetymonitor",
    "switch",
    "weather",
]


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def nina_get_all_equipment_info() -> dict:
        """Get a single combined status snapshot of every equipment category
        NINA knows about (camera, mount, filter wheel, focuser, rotator, dome,
        flat device, guider, safety monitor, switch, weather). Good first call
        to orient yourself on what's connected before doing anything else."""
        return await client.get("/equipment/info")

    @mcp.tool()
    async def nina_list_devices(device: DeviceName) -> dict:
        """List the devices NINA's device chooser sees for a given category
        (e.g. every ASCOM/native mount driver detected), each with an Id you
        can pass to `nina_connect_device`."""
        return await client.get(f"/equipment/{device}/list-devices")

    @mcp.tool()
    async def nina_connect_device(device: DeviceName, to: Optional[str] = None) -> dict:
        """Connect a piece of equipment. If `to` (a device Id from
        `nina_list_devices`) is omitted, NINA connects whichever device is
        currently selected in its own equipment dropdown for that category."""
        return await client.get(f"/equipment/{device}/connect", to=to)

    @mcp.tool()
    async def nina_disconnect_device(device: DeviceName) -> dict:
        """Disconnect a piece of equipment."""
        return await client.get(f"/equipment/{device}/disconnect")

    @mcp.tool()
    async def nina_rescan_devices(device: DeviceName) -> dict:
        """Re-scan for available devices in a given category (useful after
        plugging in USB hardware or restarting an ASCOM driver)."""
        return await client.get(f"/equipment/{device}/rescan")

    @mcp.tool()
    async def nina_get_event_history() -> list:
        """Get NINA's recent event/notification history (the same stream sent
        over its websocket), most recent first. Useful for polling status
        changes -- including Target Scheduler's TS-WAITSTART / TS-TARGETSTART
        / TS-NEWTARGETSTART events -- without holding an open websocket
        connection open from an MCP tool call."""
        return await client.get("/event-history")
