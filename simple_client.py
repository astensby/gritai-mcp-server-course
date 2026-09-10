"""Minimal MCP client (FastMCP 4).

Point it at a server with MCP_SERVER_URL; defaults to a local one so the
example works with no deployment:

    python base_server_template_http.py          # terminal 1
    python simple_client.py                      # terminal 2

    MCP_SERVER_URL="https://my-server.example.com/mcp" python simple_client.py
"""

import asyncio
import os

from fastmcp import Client

SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp/")

# Remote servers in this course sit behind OAuth; a local dev server does not.
AUTH = "oauth" if SERVER_URL.startswith("https://") else None

# mode="auto" (the default) probes for the 2026-07-28 sessionless protocol and
# falls back to the older handshake era only if the server needs it.
# mode="legacy" forces the old era - useful when a server has not upgraded.
client = Client(SERVER_URL, auth=AUTH, mode="auto")


async def main():
    async with client:
        # NOTE: there is no ping() in the 2026-07-28 protocol - the method was
        # removed along with sessions and the initialize handshake. Calling
        # client.ping() here raises "Method not found" unless you pass
        # mode="legacy". Listing tools is the connectivity check now.
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()

        print(f"Connected to {SERVER_URL}")
        print("tools:    ", [t.name for t in tools])
        print("resources:", [str(r.uri) for r in resources])
        print("prompts:  ", [p.name for p in prompts])
        print("--------------------------------")

        # Ex. execute a tool call
        # result = await client.call_tool("hello")
        # print(result)


asyncio.run(main())
