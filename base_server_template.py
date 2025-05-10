from mcp.server.fastmcp import FastMCP

mcp = FastMCP("greeting-server")

@mcp.tool()
def hello() -> str:
    """Greet the user"""
    return "Hello awesome overlord!"

if __name__ == "__main__":
    mcp.run(transport='stdio') 