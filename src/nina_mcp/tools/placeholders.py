"""Status-only equipment: safety monitor and weather station.
These categories do not have action/control endpoints defined in the API,
so they only expose status reads.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..nina_client import client


def register(mcp: FastMCP) -> None:
    # ---------------------------------------------------------------- safety monitor
    @mcp.tool()
    async def nina_safetymonitor_info() -> dict:
        """Get safety monitor status: connection and whether it currently
        reports conditions as safe.
        """
        return await client.get("/equipment/safetymonitor/info")

    # ---------------------------------------------------------------- weather
    @mcp.tool()
    async def nina_weather_info() -> dict:
        """Get weather station status: connection, cloud cover, wind,
        temperature, humidity, pressure, sky quality, rain rate (fields
        depend on what your weather device reports).
        """
        return await client.get("/equipment/weather/info")
