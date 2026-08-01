"""Sequence Templates and Calibration Workflows for N.I.N.A.

Provides high-level helpers to generate standard exposure sequences (Lights, Darks,
Flats, Biases) and load them into N.I.N.A via the Advanced API.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

from ..nina_client import client


def create_simple_item_container(
    exposure_time: float,
    count: int,
    image_type: str = "LIGHT",
    filter_name: Optional[str] = None,
    gain: Optional[int] = None,
    binning: str = "1x1",
) -> Dict[str, Any]:
    """Build a standard N.I.N.A container JSON representation for exposures."""
    return {
        "Type": "ImagingContainer",
        "ExposureCount": count,
        "ExposureTime": exposure_time,
        "ImageType": image_type.upper(),
        "Filter": filter_name or "Default",
        "Gain": gain,
        "Binning": binning,
    }


async def nina_create_calibration_sequence(
    image_type: str,
    count: int = 15,
    exposure_time: float = 0.0,
    filter_name: Optional[str] = None,
    gain: Optional[int] = None,
) -> dict:
    """Create and load a standard calibration frame sequence (DARK, FLAT, BIAS) into N.I.N.A.

    image_type: "DARK", "FLAT", "BIAS", or "DARKFLAT".
    count: number of frames to capture (default 15).
    exposure_time: length per exposure in seconds (0.0 for Bias).
    filter_name: optional filter name for Flats.
    gain: optional camera gain override.
    """
    valid_types = {"DARK", "FLAT", "BIAS", "DARKFLAT"}
    upper_type = image_type.upper()
    if upper_type not in valid_types:
        raise ValueError(f"Invalid image_type '{image_type}'. Must be one of {valid_types}")

    template = {
        "Name": f"Calibration_{upper_type}_{count}x{exposure_time}s",
        "Items": [
            create_simple_item_container(
                exposure_time=exposure_time,
                count=count,
                image_type=upper_type,
                filter_name=filter_name,
                gain=gain,
            )
        ],
    }

    # Load sequence via RAW JSON endpoint
    raw_json = json.dumps(template)
    try:
        res = await client.post_raw_body("/sequence/load", body=raw_json)
        return {
            "status": "loaded",
            "sequence_name": template["Name"],
            "image_type": upper_type,
            "count": count,
            "exposure_time": exposure_time,
            "response": res,
        }
    except Exception as e:
        # Fallback if post_raw_body expects full NINA schema
        return {
            "status": "created_template",
            "sequence_name": template["Name"],
            "image_type": upper_type,
            "count": count,
            "exposure_time": exposure_time,
            "template_json": raw_json,
            "note": f"Template generated. NINA API response: {e}",
        }


def register(mcp: FastMCP) -> None:
    mcp.tool()(nina_create_calibration_sequence)
