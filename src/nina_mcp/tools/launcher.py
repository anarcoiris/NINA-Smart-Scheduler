"""N.I.N.A Executable Discovery & Process Launcher tool.

Locates NINA.exe on the host system, checks process state, and launches N.I.N.A
asynchronously if it is not currently running.
"""

from __future__ import annotations

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP

from ..config import settings
from ..nina_client import client


STANDARD_NINA_PATHS = [
    r"%LOCALAPPDATA%\Programs\NINA\NINA.exe",
    r"%LOCALAPPDATA%\Programs\N.I.N.A\NINA.exe",
    r"%ProgramFiles%\N.I.N.A. - Nighttime Imaging 'N' Astronomy\NINA.exe",
    r"%ProgramFiles(x86)%\N.I.N.A. - Nighttime Imaging 'N' Astronomy\NINA.exe",
    r"C:\Program Files\N.I.N.A. - Nighttime Imaging 'N' Astronomy\NINA.exe",
]


def find_nina_executable(custom_path: Optional[str] = None) -> Optional[str]:
    """Search host system for NINA.exe location."""
    # 1. Check custom argument or environment variable NINA_EXE_PATH
    candidates: List[str] = []
    if custom_path:
        candidates.append(custom_path)
    env_path = os.environ.get("NINA_EXE_PATH")
    if env_path:
        candidates.append(env_path)

    # 2. Check standard Windows paths
    for p in STANDARD_NINA_PATHS:
        expanded = os.path.expandvars(p)
        candidates.append(expanded)

    for cand in candidates:
        if cand and os.path.isfile(cand):
            return str(Path(cand).resolve())

    # 3. Fallback: try `where NINA.exe` via shell
    try:
        res = subprocess.run(["where", "NINA.exe"], capture_output=True, text=True, timeout=3)
        if res.returncode == 0 and res.stdout.strip():
            first_line = res.stdout.strip().splitlines()[0]
            if os.path.isfile(first_line):
                return first_line
    except Exception:
        pass

    return None


def is_nina_process_running() -> bool:
    """Check if NINA.exe process is currently active."""
    try:
        res = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq NINA.exe", "/NH"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        return "NINA.exe" in res.stdout
    except Exception:
        return False


async def nina_ensure_running(
    custom_exe_path: Optional[str] = None,
    wait_timeout_seconds: float = 30.0,
) -> dict:
    """Check if N.I.N.A is running; if not, locate NINA.exe, launch it, and wait for Advanced API readiness.

    custom_exe_path: Optional explicit file path to NINA.exe if installed in a non-standard location.
    wait_timeout_seconds: Maximum seconds to wait for N.I.N.A's Advanced API plugin to respond after launch.
    """
    exe_path = find_nina_executable(custom_exe_path)

    # Check if API is already responding
    try:
        await client.get("/equipment/info")
        return {
            "status": "running",
            "api_ready": True,
            "executable_found": exe_path,
            "message": "N.I.N.A is running and Advanced API is responsive.",
        }
    except Exception:
        pass

    running_process = is_nina_process_running()

    if not exe_path and not running_process:
        return {
            "status": "not_found",
            "api_ready": False,
            "executable_found": None,
            "message": (
                "Could not locate NINA.exe in standard paths or PATH. "
                "Specify NINA_EXE_PATH environment variable or custom_exe_path parameter."
            ),
        }

    # If process is not running, launch it
    if not running_process and exe_path:
        try:
            subprocess.Popen([exe_path], creationflags=subprocess.DETACHED_PROCESS if os.name == "nt" else 0)
        except Exception as e:
            return {
                "status": "error",
                "api_ready": False,
                "executable_found": exe_path,
                "message": f"Failed to launch NINA.exe: {e}",
            }

    # Wait for API to respond
    start_time = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time() - start_time) < wait_timeout_seconds:
        try:
            await client.get("/equipment/info")
            return {
                "status": "started",
                "api_ready": True,
                "executable_found": exe_path,
                "message": "N.I.N.A process started and Advanced API is ready.",
            }
        except Exception:
            await asyncio.sleep(2.0)

    return {
        "status": "launching_timeout",
        "api_ready": False,
        "executable_found": exe_path,
        "message": (
            f"N.I.N.A process launched (or running), but Advanced API at {client.base_url} "
            f"did not respond within {wait_timeout_seconds}s. Make sure Advanced API plugin is enabled in N.I.N.A."
        ),
    }


def register(mcp: FastMCP) -> None:
    mcp.tool()(nina_ensure_running)
