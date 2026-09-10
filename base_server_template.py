"""Minimal FastMCP 4 server - the starting point for every example in this course.

Run it:  fastmcp dev base_server_template.py
"""

from fastmcp import FastMCP

mcp = FastMCP("greeting-server")


@mcp.tool()
def hello() -> str:
    """Greet the user"""
    return "Hello awesome overlord!"


if __name__ == "__main__":
    mcp.run(transport="stdio")
