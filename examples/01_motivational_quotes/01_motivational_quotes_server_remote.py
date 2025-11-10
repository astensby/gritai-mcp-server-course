import json
import random
import os
from fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("motivational-quotes")

def load_quotes():
    """Load quotes from the JSON file"""
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to motivational_quotes.json relative to the script
    json_file_path = os.path.join(script_dir, "motivational_quotes.json")
    with open(json_file_path, "r") as f:
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


# FastMCP supports an HTTP transport that exposes your MCP endpoint at /mcp/. 
# You can either (A) run directly with .run(transport="http"), 
# or (B) expose an ASGI app for Gunicorn/Uvicorn (typical for Azure App Service).

#LOCAL VERSION
#if __name__ == "__main__":
    # Initialize and run the server
#    mcp.run(transport='stdio') 

#REMOTE VERSION
if __name__ == "__main__":
    #mcp.run(transport="http")
    # Bind to all interfaces; port from env (Azure sets PORT for containers)
    mcp.run(transport="http", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))


#ASGI VERSION

# Expose ASGI app for Gunicorn/Uvicorn
app = mcp.http_app()

# Optional: simple health check (served at "/health")
@mcp.custom_route("/health", methods=["GET"])
async def health(_request):
    from starlette.responses import PlainTextResponse
    return PlainTextResponse("OK")