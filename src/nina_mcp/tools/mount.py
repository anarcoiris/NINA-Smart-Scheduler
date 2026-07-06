"""Mount (telescope) control. Endpoints confirmed against ninaAPI source at
WebService/V2/Equipment/Mount.cs. Connect the mount first via
`nina_connect_device(device="mount")`.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..nina_client import client

# Siderial: 0, Lunar: 1, Solar: 2, King: 3, Stopped: 4
TRACKING_MODES = {
    "sidereal": 0,
    "lunar": 1,
    "solar": 2,
    "king": 3,
    "stopped": 4,
}


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def nina_mount_info() -> dict:
        """Get full mount status: RA/Dec, altitude/azimuth, tracking state,
        parked/homed state, slewing state, site coordinates, and more."""
        return await client.get("/equipment/mount/info")

    @mcp.tool()
    async def nina_mount_home() -> dict:
        """Send the mount to its home position. Fails if not connected or
        parked (unpark first)."""
        return await client.get("/equipment/mount/home")

    @mcp.tool()
    async def nina_mount_park() -> dict:
        """Park the mount."""
        return await client.get("/equipment/mount/park")

    @mcp.tool()
    async def nina_mount_unpark() -> dict:
        """Unpark the mount."""
        return await client.get("/equipment/mount/unpark")

    @mcp.tool()
    async def nina_mount_set_tracking_mode(mode: str) -> dict:
        """Set the mount's tracking mode/rate.

        mode: one of "sidereal", "lunar", "solar", "king", "stopped".
        """
        key = mode.strip().lower()
        if key not in TRACKING_MODES:
            raise ValueError(f"mode must be one of {sorted(TRACKING_MODES)}, got {mode!r}")
        return await client.get("/equipment/mount/tracking", mode=TRACKING_MODES[key])

    @mcp.tool()
    async def nina_mount_slew(
        ra: float,
        dec: float,
        center: bool = False,
        rotate: bool = False,
        rotation_angle: float = 0.0,
        wait_for_result: bool = True,
    ) -> dict:
        """Slew the mount to J2000 RA/Dec coordinates.

        ra: Right ascension in HOURS (0-24), not degrees.
        dec: Declination in degrees (-90 to 90).
        center: if True, plate-solve and iteratively center on the target
            after the raw slew (requires camera + plate solver configured),
            instead of just a raw GOTO.
        rotate: if True, also rotate to `rotation_angle` and re-center after
            rotating (requires a connected rotator). Implies centering.
        rotation_angle: target sky position angle in degrees, only used if
            rotate=True.
        wait_for_result: if True, block until the slew (and center/rotate, if
            requested) completes and report success/failure. If False, return
            immediately once the slew has been started.
        """
        return await client.get(
            "/equipment/mount/slew",
            ra=ra,
            dec=dec,
            center=center,
            rotate=rotate,
            rotationAngle=rotation_angle,
            waitForResult=wait_for_result,
        )

    @mcp.tool()
    async def nina_mount_stop_slew() -> dict:
        """Immediately stop any in-progress slew (including a center/rotate
        started via nina_mount_slew)."""
        return await client.get("/equipment/mount/slew/stop")

    @mcp.tool()
    async def nina_mount_sync(ra: float, dec: float) -> dict:
        """Sync the mount's internal position to the given J2000 RA (hours)
        / Dec (degrees), without moving it. Used to correct pointing model
        drift once you know your true position (e.g. after a plate solve)."""
        return await client.get("/equipment/mount/sync", ra=ra, dec=dec)

    @mcp.tool()
    async def nina_mount_meridian_flip() -> dict:
        """Perform a meridian flip at the mount's current coordinates."""
        return await client.get("/equipment/mount/flip")

    @mcp.tool()
    async def nina_mount_set_park_position() -> dict:
        """Set the mount's current position as its park position. Fails if
        the mount doesn't support this or is already parked."""
        return await client.get("/equipment/mount/set-park-position")
