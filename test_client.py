"""Minimal MCP client for testing this server standalone -- no NINA, no
openclaw required. Spawns the server as a subprocess over stdio (the same way
Claude Desktop/Code or any local MCP client would), lists its tools, and
optionally calls one.

Usage:
    python test_client.py                       # list all tools
    python test_client.py nina_mount_info        # call a tool with no args
    python test_client.py nina_mount_sync ra=10.5 dec=41.2   # call with args

Args after the tool name are parsed as key=value; values are parsed as JSON
if possible (so `true`, `1.5`, `"m31"` work), otherwise kept as plain strings.
"""

from __future__ import annotations

import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PARAMS = StdioServerParameters(
    command=sys.executable,
    args=["-m", "nina_mcp.server"],
)


def _parse_value(raw: str):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


async def main() -> None:
    tool_name = sys.argv[1] if len(sys.argv) > 1 else None
    kv_args = {}
    for pair in sys.argv[2:]:
        key, _, raw_value = pair.partition("=")
        kv_args[key] = _parse_value(raw_value)

    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            if tool_name is None:
                tools = (await session.list_tools()).tools
                print(f"{len(tools)} tools available:\n")
                for t in tools:
                    print(f"- {t.name}: {t.description.splitlines()[0] if t.description else ''}")
                return

            result = await session.call_tool(tool_name, kv_args)
            for block in result.content:
                if hasattr(block, "text"):
                    print(block.text)
                else:
                    print(block)


if __name__ == "__main__":
    asyncio.run(main())
