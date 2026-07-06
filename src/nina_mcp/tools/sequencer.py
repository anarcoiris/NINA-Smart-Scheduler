"""Advanced Sequencer control. Endpoints confirmed against ninaAPI source at
WebService/V2/Application/Sequence.cs.

This is also how you run a Target Scheduler-driven session: load/open a
sequence in NINA that contains a "Target Scheduler Container" instruction
(built in the NINA UI, not via this API), then call nina_sequence_start.
See tools/target_scheduler.py for why TS itself has no REST control surface.
"""

from __future__ import annotations

from typing import Literal, Optional

from mcp.server.fastmcp import FastMCP

from ..nina_client import client

SkipType = Literal["CurrentItems", "ToEnd", "ToImaging"]


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def nina_sequence_get_json() -> dict:
        """Get the currently loaded Advanced Sequence as NINA's own JSON
        structure (containers, instructions, triggers, conditions)."""
        return await client.get("/sequence/json")

    @mcp.tool()
    async def nina_sequence_get_state() -> dict:
        """Get the current run state of the loaded sequence: which item is
        executing, overall progress, and whether it's running/stopped."""
        return await client.get("/sequence/state")

    @mcp.tool()
    async def nina_sequence_start(skip_validation: bool = False) -> dict:
        """Start running the currently loaded Advanced Sequence.

        skip_validation: skip NINA's pre-flight validation checks (equipment
            connected, safe to image, etc). Leave False unless you have a
            good reason.
        """
        return await client.get("/sequence/start", skipValidation=skip_validation)

    @mcp.tool()
    async def nina_sequence_stop() -> dict:
        """Stop the currently running sequence."""
        return await client.get("/sequence/stop")

    @mcp.tool()
    async def nina_sequence_reset() -> dict:
        """Reset the loaded sequence back to its initial, not-yet-run state."""
        return await client.get("/sequence/reset")

    @mcp.tool()
    async def nina_sequence_skip(skip_type: SkipType) -> dict:
        """Skip ahead in the running sequence.

        skip_type: "CurrentItems" (skip just the current instruction(s)),
            "ToEnd" (skip to the end area / shutdown), or "ToImaging" (skip
            straight to the imaging area).
        """
        return await client.get("/sequence/skip", type=skip_type)

    @mcp.tool()
    async def nina_sequence_edit(path: str, value: str) -> dict:
        """Edit a single field of the loaded sequence in place, addressed by
        path (as shown in `nina_sequence_get_json`'s structure). Useful for
        small tweaks (e.g. an exposure count or duration) without reloading
        the whole sequence."""
        return await client.get("/sequence/edit", path=path, value=value)

    @mcp.tool()
    async def nina_sequence_list_available() -> dict:
        """List sequence files available in NINA's default sequence folder,
        loadable by name via `nina_sequence_load_by_name`."""
        return await client.get("/sequence/list-available")

    @mcp.tool()
    async def nina_sequence_load_by_name(sequence_name: str) -> dict:
        """Load a saved sequence (by name, without the .json extension) from
        NINA's default sequence folder as the active Advanced Sequence. Fails
        if a sequence is currently running."""
        return await client.get("/sequence/load", sequenceName=sequence_name)

    @mcp.tool()
    async def nina_sequence_load_json(sequence_json: str) -> dict:
        """Load an entire Advanced Sequence from a raw JSON string (NINA's
        own sequence export format, as returned by `nina_sequence_get_json`).
        Fails if a sequence is currently running."""
        return await client.post_raw_body("/sequence/load", body=sequence_json)

    @mcp.tool()
    async def nina_sequence_set_target(
        name: str, ra: float, dec: float, rotation: float = 0.0, index: int = 0
    ) -> dict:
        """Update the coordinates/name/rotation of a DSO target container
        already present in the loaded sequence.

        name: display name for the target.
        ra: J2000 right ascension in hours.
        dec: J2000 declination in degrees.
        rotation: target sky position angle in degrees.
        index: which target container to update, if the sequence has more
            than one (0-based).
        """
        return await client.get(
            "/sequence/set-target", name=name, ra=ra, dec=dec, rotation=rotation, index=index
        )
