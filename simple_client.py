import asyncio
from fastmcp import Client, FastMCP

client = Client("http://localhost:8000/mcp")
#client = Client("http://localhost:8000/mcp", auth="oauth")

async def main():
    async with client:
        # Ensure client can connect
        await client.ping()

        # List available operations
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()

        # Ex. execute a tool call
        result = await client.call_tool("hello")
        print(result)

asyncio.run(main())