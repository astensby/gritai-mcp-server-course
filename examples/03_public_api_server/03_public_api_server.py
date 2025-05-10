import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("police-incidents", dependencies=["requests"])

def get_latest_incidents() -> str:
    """Fetch the latest incidents from the Politiet API"""
    url = 'https://api.politiet.no/politiloggen/v1/messages'
    headers = {'accept': 'text/plain'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching incidents: {e}")
        return f"Error fetching incidents: {e}"

def get_incidents_by_municipality(municipality: str) -> str:
    """Fetch incidents for a specific municipality from the Politiet API"""
    url = 'https://api.politiet.no/politiloggen/v1/messages'
    headers = {'accept': 'text/plain'}
    params = {'Municipalities': municipality}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching incidents for {municipality}: {e}")
        return f"Error fetching incidents for {municipality}: {e}"

@mcp.tool()
def latest_incidents() -> str:
    """Get the 10 latest police incidents"""
    incidents = get_latest_incidents()
    return incidents

@mcp.tool()
def incidents_by_municipality(municipality: str) -> str:
    """Get the latest police incidents for a specific municipality.
    
    Args:
        municipality: The municipality to fetch incidents for.
    """
    incidents = get_incidents_by_municipality(municipality)
    return incidents

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio') 