"""The same server over HTTP instead of stdio.

Only the transport changes. "http" is Streamable HTTP, the transport the
2026-07-28 protocol revision standardises on; "sse" still exists but is
formally deprecated and scheduled for removal.

Run it:  python base_server_template_http.py   (serves on http://127.0.0.1:8000/mcp/)
"""

import os

from fastmcp import FastMCP

mcp = FastMCP("greeting-server")


@mcp.tool()
def hello() -> str:
    """Greet the user"""
    return "Hello awesome overlord!"


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=int(os.getenv("PORT", "8000")))
