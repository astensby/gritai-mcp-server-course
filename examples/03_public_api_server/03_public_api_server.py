import requests
from fastmcp import FastMCP

mcp = FastMCP("police-incidents")

POLITILOGGEN_URL = "https://api.politiloggen.politiet.no/messages"


def get_latest_incidents() -> str:
    """Fetch the latest incidents from the Politiet API"""
    headers = {"accept": "text/plain"}
    try:
        response = requests.get(POLITILOGGEN_URL, headers=headers, timeout=15)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching incidents: {e}"


def get_incidents_by_municipality(municipality: str) -> str:
    """Fetch incidents for a specific municipality from the Politiet API"""
    headers = {"accept": "text/plain"}
    params = {"Municipalities": municipality}
    try:
        response = requests.get(POLITILOGGEN_URL, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching incidents for {municipality}: {e}"


@mcp.tool()
def latest_incidents() -> str:
    """Get the latest police incidents from anywhere in Norway."""
    return get_latest_incidents()


@mcp.tool()
def incidents_by_municipality(municipality: str) -> str:
    """Get the latest police incidents for a specific municipality.

    Args:
        municipality: The municipality to fetch incidents for.
    """
    return get_incidents_by_municipality(municipality)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
