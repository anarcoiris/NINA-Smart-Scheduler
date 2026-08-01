"""Aggregated System Status & Telemetry report for N.I.N.A astrophotography rig.

Provides a unified status overview of all connected equipment, mount coordinates,
camera cooler state, target, and guiding status.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP

from ..nina_client import client, NinaAPIError


async def _safe_get(path: str) -> Dict[str, Any]:
    try:
        res = await client.get(path)
        if isinstance(res, dict):
            return res
        return {"data": res, "connected": True}
    except NinaAPIError as e:
        return {"connected": False, "error": str(e)}
    except Exception as e:
        return {"connected": False, "error": f"Unexpected error: {e}"}


async def nina_get_system_status() -> dict:
    """Get an aggregated high-level status report of the entire astrophotography rig.

    Queries connected devices (Camera, Mount, Focuser, FilterWheel, Guider, Dome, Weather)
    in parallel and consolidates overall operational telemetry into a single status report.
    """
    results = await asyncio.gather(
        _safe_get("/equipment/info"),
        _safe_get("/equipment/camera/info"),
        _safe_get("/equipment/mount/info"),
        _safe_get("/equipment/focuser/info"),
        _safe_get("/equipment/filterwheel/info"),
        _safe_get("/equipment/guider/info"),
        _safe_get("/equipment/dome/info"),
        return_exceptions=True,
    )

    all_equipment, camera_info, mount_info, focuser_info, filterwheel_info, guider_info, dome_info = results

    # Build clean summary
    summary = {
        "api_endpoint": client.base_url,
        "equipment_summary": all_equipment if isinstance(all_equipment, dict) else {},
        "devices": {
            "camera": camera_info if isinstance(camera_info, dict) else {},
            "mount": mount_info if isinstance(mount_info, dict) else {},
            "focuser": focuser_info if isinstance(focuser_info, dict) else {},
            "filterwheel": filterwheel_info if isinstance(filterwheel_info, dict) else {},
            "guider": guider_info if isinstance(guider_info, dict) else {},
            "dome": dome_info if isinstance(dome_info, dict) else {},
        },
    }
    return summary


def register(mcp: FastMCP) -> None:
    mcp.tool()(nina_get_system_status)
