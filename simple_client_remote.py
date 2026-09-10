"""Client for a remote, OAuth-protected MCP server.

Same client as simple_client.py, pointed at a deployed server instead of
localhost. The only real difference is `auth="oauth"`: on first run FastMCP
opens a browser for the OAuth flow and caches the token, so subsequent runs
are silent.

Set the URL of a server you control - there is no default, because a remote
server is yours to deploy (FastMCP Cloud, Azure App Service, a container):

    export MCP_SERVER_URL="https://<your-server>.fastmcp.app/mcp"
    uv run simple_client_remote.py

    # Call a specific tool instead of just listing what is available:
    MCP_TOOL=random_quote uv run simple_client_remote.py
    MCP_TOOL=echo_tool MCP_TOOL_ARGS='{"text": "Hello, world!"}' uv run simple_client_remote.py

Example 08 (examples/08_azure_auth_remote_server/) is a server you can deploy
and point this at.
"""

import asyncio
import json
import os
import sys

from fastmcp import Client

SERVER_URL = os.getenv("MCP_SERVER_URL")
if not SERVER_URL:
    print(
        "Set MCP_SERVER_URL to your deployed server, e.g.\n"
        '    export MCP_SERVER_URL="https://<your-server>.fastmcp.app/mcp"',
        file=sys.stderr,
    )
    sys.exit(1)

# mode="auto" (the default) speaks the 2026-07-28 sessionless protocol and
# falls back to the handshake era only if the server needs it.
client = Client(SERVER_URL, auth="oauth", mode="auto")


async def main():
    async with client:
        # No ping() on the 2026-07-28 protocol - list_tools() is the check.
        tools = await client.list_tools()
        print(f"Connected to {SERVER_URL}")
        print("tools:", [t.name for t in tools])

        tool_name = os.getenv("MCP_TOOL")
        if not tool_name:
            print("\nSet MCP_TOOL=<name> to call one of the tools above.")
            return

        arguments = json.loads(os.getenv("MCP_TOOL_ARGS", "{}"))
        result = await client.call_tool(tool_name, arguments)
        print(f"\n{tool_name} ->")
        print(result)


asyncio.run(main())
