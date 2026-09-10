"""Example 01, served over HTTP instead of stdio (e.g. Azure App Service).

Two ways to serve the same server:
  (A) run it directly          -> python 01_motivational_quotes_server_remote.py
  (B) hand the ASGI app to a   -> uvicorn 01_motivational_quotes_server_remote:app
      process manager             (gunicorn/uvicorn, typical for Azure App Service)

Note the ordering below: custom routes must be registered BEFORE http_app()
is called, or they are missing from the ASGI app that gets served.
"""

import json
import os
import random

from fastmcp import FastMCP
from starlette.responses import PlainTextResponse

# Create an MCP server
mcp = FastMCP("motivational-quotes")


def load_quotes():
    """Load quotes from the JSON file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, "motivational_quotes.json")
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["quotes"]


# Load quotes when the server starts
quotes = load_quotes()


@mcp.tool()
def random_quote() -> str:
    """Get a random motivational quote"""
    quote_data = random.choice(quotes)
    return f"\"{quote_data['quote']}\" - {quote_data['author']}"


@mcp.prompt()
def funny_quote(quote: str) -> str:
    """Turns a motivational quote into a funny motivational quote"""
    return f"Please turn this quote into a funny motivational quote:\n\n{quote}"


# Simple health check (served at "/health") - registered before http_app().
@mcp.custom_route("/health", methods=["GET"])
async def health(_request):
    return PlainTextResponse("OK")


# (B) ASGI app for gunicorn/uvicorn. Must come after every route registration.
app = mcp.http_app()


# (A) Run directly. Bind to all interfaces; Azure supplies PORT for containers.
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
