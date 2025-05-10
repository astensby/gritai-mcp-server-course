import random
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("basic-finance-server")

@mcp.resource("stock://{symbol}/earnings")
def earnings(symbol: str) -> str:
    """Get the earnings for a stock"""
    return f"The earnings for {symbol} are {random.randint(1000000, 1000000000)}"

@mcp.resource("stock://earnings")
def latest_NVIDIA_earnings() -> str:
    """Get the latest earnings for NVIDIA"""
    return f"The latest earnings for NVIDIA are {random.randint(1000000, 1000000000)}"


@mcp.prompt()
def earnings_summary(symbol: str, earnings: str) -> str:
    """Summarize the earnings for a stock"""
    return f"You are an expert financial analyst. Please summarize the earnings for {symbol} which are {earnings}"


@mcp.tool()
def calculate_cagr(symbol: str, years: int, start_price: float, end_price: float) -> str:
    """Calculate the CAGR for a stock"""
    cagr = ((end_price / start_price) ** (1 / years)) - 1
    return f"The CAGR for {symbol} over {years} years is {cagr:.2%}"


if __name__ == "__main__":
    mcp.run(transport='stdio') 