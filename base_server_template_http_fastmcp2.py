from fastmcp import FastMCP
import os
mcp = FastMCP("greeting-server")

@mcp.tool()
def hello() -> str:
    """Greet the user"""
    return "Hello awesome overlord!"

if __name__ == "__main__":
    mcp.run(transport='streamable-http')    
    #mcp.run(transport="streamable-http", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))


    
 