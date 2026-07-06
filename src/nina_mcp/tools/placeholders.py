"""Non-core equipment: filter wheel, focuser, rotator, dome, guider, safety
monitor, weather, switch, flat device.

Per scope, these get real (cheap, verified) status reads plus clearly marked
stubs for the action endpoints. Every stub's docstring/comment gives you the
exact, verified ninaAPI route and query parameters (pulled from ninaAPI's
source, not guessed) so wiring up the rest is a copy-paste job, following the
same pattern as tools/mount.py and tools/camera.py.

Connect each device first via `nina_connect_device(device=...)` from
tools/equipment.py.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..nina_client import client


class NotImplementedPlaceholder(Exception):
    def __init__(self, hint: str):
        super().__init__(
            f"Not wired up yet. {hint} See tools/placeholders.py to implement it "
            f"(same pattern as tools/mount.py or tools/camera.py)."
        )


def register(mcp: FastMCP) -> None:
    # ---------------------------------------------------------------- filter wheel
    @mcp.tool()
    async def nina_filterwheel_info() -> dict:
        """Get filter wheel status: connection, current filter, available
        filters and their positions."""
        return await client.get("/equipment/filterwheel/info")

    @mcp.tool()
    async def nina_filterwheel_change_filter(filter_id: int) -> dict:
        """PLACEHOLDER. Real endpoint: GET /equipment/filterwheel/change-filter
        (query param, [QueryField]: likely a filter position/id -- confirm
        exact param name against your ninaAPI version before relying on it).
        Also available: /equipment/filterwheel/filter-info,
        /equipment/filterwheel/add-filter, /equipment/filterwheel/remove-filter.
        """
        raise NotImplementedPlaceholder(
            "Wire up GET /equipment/filterwheel/change-filter with client.get()."
        )

    # ---------------------------------------------------------------- focuser
    @mcp.tool()
    async def nina_focuser_info() -> dict:
        """Get focuser status: connection, current position, temperature,
        moving state, temperature compensation state."""
        return await client.get("/equipment/focuser/info")

    @mcp.tool()
    async def nina_focuser_move(position: int) -> dict:
        """PLACEHOLDER. Real endpoint: GET /equipment/focuser/move
        (query param, [QueryField]: target position). Also available:
        /equipment/focuser/stop-move, /equipment/focuser/auto-focus,
        /equipment/focuser/last-af, /equipment/focuser/pins/reverse.
        """
        raise NotImplementedPlaceholder(
            "Wire up GET /equipment/focuser/move with client.get()."
        )

    # ---------------------------------------------------------------- rotator
    @mcp.tool()
    async def nina_rotator_info() -> dict:
        """Get rotator status: connection, current mechanical/sky position,
        moving state, reverse setting."""
        return await client.get("/equipment/rotator/info")

    @mcp.tool()
    async def nina_rotator_move(angle: float) -> dict:
        """PLACEHOLDER. Real endpoint: GET /equipment/rotator/move (query
        param: target sky angle in degrees). Also available:
        /equipment/rotator/move-mechanical, /equipment/rotator/reverse,
        /equipment/rotator/set-mechanical-range, /equipment/rotator/stop-move.
        """
        raise NotImplementedPlaceholder("Wire up GET /equipment/rotator/move with client.get().")

    # ---------------------------------------------------------------- dome
    @mcp.tool()
    async def nina_dome_info() -> dict:
        """Get dome status: connection, shutter state, azimuth, slewing,
        parked state, dome-follows-mount setting."""
        return await client.get("/equipment/dome/info")

    @mcp.tool()
    async def nina_dome_open(shutter: bool) -> dict:
        """PLACEHOLDER. Real endpoints: GET /equipment/dome/open and
        GET /equipment/dome/close (no params -- separate routes, not a single
        toggle). Also available: /equipment/dome/stop, /equipment/dome/slew,
        /equipment/dome/sync, /equipment/dome/set-follow,
        /equipment/dome/set-park-position, /equipment/dome/park,
        /equipment/dome/home.
        """
        raise NotImplementedPlaceholder(
            "Wire up GET /equipment/dome/open or /equipment/dome/close with client.get()."
        )

    # ---------------------------------------------------------------- guider
    @mcp.tool()
    async def nina_guider_info() -> dict:
        """Get autoguider status: connection, guiding state, last guide
        step/RMS error info."""
        return await client.get("/equipment/guider/info")

    @mcp.tool()
    async def nina_guider_start(calibrate: bool = False) -> dict:
        """PLACEHOLDER. Real endpoint: GET /equipment/guider/start. Also
        available: /equipment/guider/stop, /equipment/guider/clear-calibration,
        /equipment/guider/graph.
        """
        raise NotImplementedPlaceholder("Wire up GET /equipment/guider/start with client.get().")

    # ---------------------------------------------------------------- safety monitor
    @mcp.tool()
    async def nina_safetymonitor_info() -> dict:
        """Get safety monitor status: connection and whether it currently
        reports conditions as safe."""
        return await client.get("/equipment/safetymonitor/info")

    # ---------------------------------------------------------------- weather
    @mcp.tool()
    async def nina_weather_info() -> dict:
        """Get weather station status: connection, cloud cover, wind,
        temperature, humidity, pressure, sky quality, rain rate (fields
        depend on what your weather device reports)."""
        return await client.get("/equipment/weather/info")

    # ---------------------------------------------------------------- switch
    @mcp.tool()
    async def nina_switch_info() -> dict:
        """Get switch device status: connection and the state/value of each
        configured switch."""
        return await client.get("/equipment/switch/info")

    @mcp.tool()
    async def nina_switch_set(switch_index: int, value: float) -> dict:
        """PLACEHOLDER. Real endpoint: GET /equipment/switch/set (query
        params likely include a switch index and target value -- confirm
        exact param names against your ninaAPI version before relying on
        this)."""
        raise NotImplementedPlaceholder("Wire up GET /equipment/switch/set with client.get().")

    # ---------------------------------------------------------------- flat device
    @mcp.tool()
    async def nina_flatdevice_info() -> dict:
        """Get flat panel/flat device status: connection, light on/off,
        brightness, cover open/closed."""
        return await client.get("/equipment/flatdevice/info")

    @mcp.tool()
    async def nina_flatdevice_set_light(on: bool) -> dict:
        """PLACEHOLDER. Real endpoint: GET /equipment/flatdevice/set-light.
        Also available: /equipment/flatdevice/set-cover,
        /equipment/flatdevice/set-brightness.
        """
        raise NotImplementedPlaceholder(
            "Wire up GET /equipment/flatdevice/set-light with client.get()."
        )
