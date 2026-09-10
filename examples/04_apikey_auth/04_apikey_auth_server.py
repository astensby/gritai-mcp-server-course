import os

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("investment-data")


def get_ticker(company_name: str) -> str:
    """Fetches the stock ticker for a given company name using the Alpha Vantage API."""
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        raise ValueError("ALPHAVANTAGE_API_KEY environment variable not set.")

    url = "https://www.alphavantage.co/query"
    params = {"function": "SYMBOL_SEARCH", "keywords": company_name, "apikey": api_key}

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()

        if "bestMatches" in data and data["bestMatches"]:
            ticker = data["bestMatches"][0].get("1. symbol")
            if ticker:
                return ticker
            raise ValueError("Could not find ticker symbol in API response.")

        if "Note" in data:
            raise ValueError(f"API call frequency limit reached or other note: {data['Note']}")
        raise ValueError(f"No ticker found for '{company_name}'. API Response: {data}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Error connecting to Alpha Vantage API: {e}")


@mcp.tool()
def ticker_search(company_name: str) -> str:
    """Get the ticker for a company

    Args:
        company_name: The name of the company to search for

    Returns:
        The ticker for the company

    Example:
            ticker_search("Apple") -> "AAPL"
    """
    return get_ticker(company_name)


if __name__ == "__main__":
    mcp.run(transport="stdio")
