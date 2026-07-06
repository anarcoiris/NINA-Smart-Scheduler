"""Camera control. Endpoints confirmed against ninaAPI source at
WebService/V2/Equipment/Camera.cs. Connect the camera first via
`nina_connect_device(device="camera")`.
"""

from __future__ import annotations

from typing import Optional

from mcp.server.fastmcp import FastMCP

from ..nina_client import client


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def nina_camera_info() -> dict:
        """Get full camera status: connection state, cooler on/off, current
        and target temperature, cooler power, gain/offset, binning, readout
        mode, and capabilities."""
        return await client.get("/equipment/camera/info")

    @mcp.tool()
    async def nina_camera_capture(
        duration: float,
        gain: Optional[int] = None,
        save: bool = True,
        target_name: Optional[str] = None,
        image_type: Optional[str] = None,
        solve: bool = False,
        wait_for_result: bool = True,
        only_await_capture_completion: bool = False,
        get_result: bool = False,
        omit_image: bool = True,
        resize: bool = False,
        size: Optional[str] = None,
        quality: Optional[int] = None,
        scale: Optional[float] = None,
        stream: bool = False,
        only_save_raw: bool = False,
        skip_auto_stretch: bool = False,
    ) -> dict:
        """Capture a single exposure.

        duration: exposure length in seconds.
        gain: camera gain; omit to use the camera's current/default gain.
        save: whether to save the resulting image to disk.
        target_name: subfolder/name association for the saved file, if any.
        image_type: e.g. "LIGHT", "DARK", "FLAT", "BIAS" (NINA's own image
            type strings); omit to use the current default.
        solve: plate-solve the resulting image.
        wait_for_result: block until the exposure (and any requested
            download/processing) finishes.
        only_await_capture_completion: return as soon as the exposure itself
            finishes, without waiting for download/processing -- use with
            wait_for_result=True.
        get_result: include image statistics/metadata in the response.
        omit_image: don't include the actual image data (base64) in the
            response -- keep this True unless you specifically want the pixel
            data returned inline, since it can be large.
        resize / size / quality / scale: control a resized preview image if
            omit_image=False (size like "1920x1080", quality 1-100).
        stream: stream the image back as it's captured rather than after.
        only_save_raw: save only the raw sensor data, skipping NINA's normal
            processing pipeline.
        skip_auto_stretch: skip auto-stretch when producing a preview image.
        """
        return await client.get(
            "/equipment/camera/capture",
            duration=duration,
            gain=gain,
            save=save,
            targetName=target_name,
            imageType=image_type,
            solve=solve,
            waitForResult=wait_for_result,
            onlyAwaitCaptureCompletion=only_await_capture_completion,
            getResult=get_result,
            omitImage=omit_image,
            resize=resize,
            size=size,
            quality=quality,
            scale=scale,
            stream=stream,
            onlySaveRaw=only_save_raw,
            skipAutoStretch=skip_auto_stretch,
        )

    @mcp.tool()
    async def nina_camera_abort_exposure() -> dict:
        """Abort the exposure currently in progress."""
        return await client.get("/equipment/camera/abort-exposure")

    @mcp.tool()
    async def nina_camera_capture_statistics() -> dict:
        """Get statistics (HFR, star count, mean ADU, etc.) for the most
        recently captured image."""
        return await client.get("/equipment/camera/capture/statistics")

    @mcp.tool()
    async def nina_camera_cool(
        temperature: float, minutes: Optional[float] = None, cancel: bool = False
    ) -> dict:
        """Start cooling the camera to a target temperature (°C).

        temperature: target sensor temperature in Celsius.
        minutes: cool down over this many minutes rather than immediately, if
            supported by the camera.
        cancel: if True, cancel an in-progress cooldown instead of starting
            one (temperature/minutes are ignored in that case).
        """
        return await client.get(
            "/equipment/camera/cool", temperature=temperature, minutes=minutes, cancel=cancel
        )

    @mcp.tool()
    async def nina_camera_warm(minutes: Optional[float] = None, cancel: bool = False) -> dict:
        """Warm the camera back up (turn off/ramp down the cooler).

        minutes: warm up over this many minutes rather than immediately.
        cancel: if True, cancel an in-progress warmup instead of starting one.
        """
        return await client.get("/equipment/camera/warm", minutes=minutes, cancel=cancel)

    @mcp.tool()
    async def nina_camera_set_binning(binning: str) -> dict:
        """Set camera binning, e.g. "1x1", "2x2", "3x3"."""
        return await client.get("/equipment/camera/set-binning", binning=binning)

    @mcp.tool()
    async def nina_camera_set_readout_mode(mode: int) -> dict:
        """Set the camera's readout mode index (camera-specific; see
        nina_camera_info for the list of supported modes)."""
        return await client.get("/equipment/camera/set-readout", mode=mode)

    @mcp.tool()
    async def nina_camera_set_dew_heater(power: bool) -> dict:
        """Turn the camera's dew heater on (True) or off (False), if the
        camera has one."""
        return await client.get("/equipment/camera/dew-heater", power=power)

    @mcp.tool()
    async def nina_camera_set_usb_limit(limit: int) -> dict:
        """Set the camera's USB bandwidth/traffic limit, if supported."""
        return await client.get("/equipment/camera/usb-limit", limit=limit)
