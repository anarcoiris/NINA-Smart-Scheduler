"""Nighttime'N'Astroagents — Standalone Autonomous Astrophotography Agent Runtime.

Can run completely standalone on the observatory PC or remote rig without external dependencies.
Connects local LLMs (Qwythos llama.cpp on :11440, Ollama on :11434, or OpenAI-compatible endpoint)
directly to N.I.N.A Advanced API tools.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
import httpx

# Ensure src in sys.path
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from nina_mcp.nina_client import client as nina_client
from nina_mcp.tools.launcher import nina_ensure_running
from nina_mcp.tools.system_status import nina_get_system_status
from nina_mcp.tools.sequence_templates import nina_create_calibration_sequence


# Define clean async tool wrappers for standalone agent dispatch
async def nina_mount_slew(ra: float, dec: float, slew_and_center: bool = True) -> dict:
    return await nina_client.get("/equipment/mount/slew", ra=ra, dec=dec, slewAndCenter=slew_and_center)

async def nina_mount_park() -> dict:
    return await nina_client.get("/equipment/mount/park")

async def nina_mount_home() -> dict:
    return await nina_client.get("/equipment/mount/home")

async def nina_camera_capture(duration: float, save: bool = True, target_name: Optional[str] = None, image_type: str = "LIGHT") -> dict:
    return await nina_client.get("/equipment/camera/capture", duration=duration, save=save, targetName=target_name, imageType=image_type, getResult=True, omitImage=True)

async def nina_camera_cool(temperature: float) -> dict:
    return await nina_client.get("/equipment/camera/cool", temperature=temperature)

async def nina_focuser_autofocus() -> dict:
    return await nina_client.get("/equipment/focuser/autofocus")

async def nina_sequence_start() -> dict:
    return await nina_client.get("/sequence/start")

async def nina_sequence_stop() -> dict:
    return await nina_client.get("/sequence/stop")


TOOL_MAP = {
    "nina_ensure_running": nina_ensure_running,
    "nina_get_system_status": nina_get_system_status,
    "nina_mount_slew": nina_mount_slew,
    "nina_mount_park": nina_mount_park,
    "nina_mount_home": nina_mount_home,
    "nina_camera_capture": nina_camera_capture,
    "nina_camera_cool": nina_camera_cool,
    "nina_focuser_autofocus": nina_focuser_autofocus,
    "nina_create_calibration_sequence": nina_create_calibration_sequence,
    "nina_sequence_start": nina_sequence_start,
    "nina_sequence_stop": nina_sequence_stop,
}


SYSTEM_PROMPT = """You are Nighttime'N'Astroagents, an autonomous astrophotography copilot for N.I.N.A.
You control telescope mounts, cameras, focusers, filter wheels, and sequencers.

When a user asks to perform an action, respond with a JSON block requesting tool execution in this exact format:
```json
{
  "tool": "tool_name",
  "args": { ... }
}
```
Available tools:
- nina_ensure_running(): Ensure NINA.exe is running and API is ready.
- nina_get_system_status(): Get status of all connected devices.
- nina_mount_slew(ra: float, dec: float, slew_and_center: bool=True): Slew to coordinates.
- nina_mount_park(): Park telescope mount.
- nina_camera_capture(duration: float, save: bool=True, target_name: str=None, image_type: str="LIGHT"): Take exposure.
- nina_camera_cool(temperature: float): Set camera cooling.
- nina_focuser_autofocus(): Run HFR autofocus routine.
- nina_create_calibration_sequence(image_type: str, count: int, exposure_time: float): Create Darks/Flats/Biases.
- nina_sequence_start(): Start current sequence.
- nina_sequence_stop(): Stop active sequence.
"""


class StandaloneAstroAgent:
    def __init__(self, llm_base_url: Optional[str] = None, model: Optional[str] = None):
        self.llm_base_url = (llm_base_url or os.environ.get("LLM_BASE_URL") or "http://127.0.0.1:11440/v1").rstrip("/")
        self.model = model or os.environ.get("LLM_MODEL") or "qwythos"
        self._http_client = httpx.AsyncClient(timeout=120.0)

    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        if tool_name not in TOOL_MAP:
            return {"error": f"Unknown tool '{tool_name}'"}
        try:
            fn = TOOL_MAP[tool_name]
            if asyncio.iscoroutinefunction(fn):
                return await fn(**args)
            return fn(**args)
        except Exception as e:
            return {"error": str(e)}

    async def run_prompt(self, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        try:
            resp = await self._http_client.post(
                f"{self.llm_base_url}/chat/completions",
                json={"model": self.model, "messages": messages, "temperature": 0.1},
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]

            # Parse tool call if present
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
                call_data = json.loads(json_str)
                tool_name = call_data.get("tool")
                tool_args = call_data.get("args", {})
                result = await self.execute_tool(tool_name, tool_args)
                return f"Executed `{tool_name}` with args {tool_args}.\nResult:\n```json\n{json.dumps(result, indent=2)}\n```"

            return content
        except Exception as e:
            # Fallback if local LLM is not running right now: execute tool directly for CLI testing
            if "get_system_status" in user_prompt.lower() or "estado" in user_prompt.lower():
                status_res = await self.execute_tool("nina_get_system_status", {})
                return f"Local LLM Offline ({e}). Direct Telemetry Execution Result:\n```json\n{json.dumps(status_res, indent=2)}\n```"
            return f"Agent Error: {e}"


async def main():
    agent = StandaloneAstroAgent()
    print("=========================================================================")
    print("   [Nighttime'N'Astroagents] Standalone Autonomous Agent Runtime")
    print("=========================================================================")
    print(f"Connecting to LLM at: {agent.llm_base_url}")
    print(f"Connecting to N.I.N.A API at: {nina_client.base_url}\n")

    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Comprobar estado general del telescopio y NINA"
    print(f"User Prompt: {prompt}")
    res = await agent.run_prompt(prompt)
    print(f"\nResponse:\n{res}")


if __name__ == "__main__":
    asyncio.run(main())
