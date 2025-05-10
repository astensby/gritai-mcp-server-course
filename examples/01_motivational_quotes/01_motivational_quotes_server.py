import json
import random
import os
from mcp.server.fastmcp import FastMCP

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


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio') 