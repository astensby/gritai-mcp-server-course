import os
import json
import random
from typing import Dict, List, Any

from dotenv import load_dotenv

from fastmcp import FastMCP
from fastmcp.server.auth.providers.azure import AzureProvider

from starlette.requests import Request
from starlette.responses import PlainTextResponse

# Load environment variables from a local .env file if present
load_dotenv()

# --- OAuth (Azure Entra ID) via FastMCP AzureProvider ---
auth_server_provider = None
if os.getenv("ENABLE_OIDC", "1") == "1":
    required = ["AZURE_TENANT_ID", "OIDC_CLIENT_ID", "OIDC_CLIENT_SECRET", "PUBLIC_BASE_URL"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(f"[WARN] Missing env vars for Azure OAuth ({', '.join(missing)}); starting without OAuth.")
    else:
        public_base_url = os.environ["PUBLIC_BASE_URL"]
        # Optional overrides
        redirect_path = os.getenv("OIDC_REDIRECT_PATH", "/auth/callback")
        # Allow common loopback redirects by default; override with OIDC_ALLOWED_REDIRECT_URIS (comma-separated)
        allowed_redirects_env = os.getenv("OIDC_ALLOWED_REDIRECT_URIS")
        if allowed_redirects_env:
            allowed_redirects = [u.strip() for u in allowed_redirects_env.split(",") if u.strip()]
        else:
            allowed_redirects = [
                "http://localhost:*/*",
                "http://127.0.0.1:*/*",
            ]

        default_required_scopes=[
                    "User.Read", "email", "openid", "profile", "offline_access"
                ]

        # Scopes (defaults align with AzureProvider)
        scopes_env = os.getenv("OIDC_REQUIRED_SCOPES")
        required_scopes = [s for s in scopes_env.split() if s] if scopes_env else default_required_scopes

        try:
            # The AzureProvider handles Azure's token format and validation
            auth_server_provider = AzureProvider(
                client_id=os.environ["OIDC_CLIENT_ID"], # Your Azure App Client ID
                client_secret=os.environ["OIDC_CLIENT_SECRET"], # Your Azure App Client Secret
                tenant_id=os.environ["AZURE_TENANT_ID"], # Your Azure Tenant ID (REQUIRED)
                base_url=public_base_url,                   # Must match your App registration                
                # redirect_path="/auth/callback"                  # Default value, customize if needed
                # redirect_path=redirect_path,
                #allowed_client_redirect_uris=allowed_redirects,
                required_scopes=required_scopes,
            )

        except Exception as e:
            print("[WARN] Failed to configure Azure OAuth; starting without OAuth. Error:", e)
            auth_server_provider = None


# ----------------- MCP Server -----------------

mcp = FastMCP(name="motivational-quotes", auth=auth_server_provider)

# Add a protected tool to test authentication
@mcp.tool()
async def get_user_info() -> dict:
    """Returns information about the authenticated Azure user."""
    from fastmcp.server.dependencies import get_access_token
    
    token = get_access_token()
    # The AzureProvider stores user data in token claims
    return {
        "azure_id": token.claims.get("sub"),
        "email": token.claims.get("email"),
        "name": token.claims.get("name"),
        "job_title": token.claims.get("job_title"),
        "office_location": token.claims.get("office_location")
    }

def load_quotes():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, "motivational_quotes.json")
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["quotes"]

quotes = load_quotes()

@mcp.tool()
def random_quote() -> str:
    """
    Random quote tool returning a single quote.

    Args:
        None

    Returns:
        Single quote with quote and author.
    """
    q = random.choice(quotes)
    return f"\"{q['quote']}\" - {q['author']}"

# -------------------------------
#           SEARCH tool
# -------------------------------
@mcp.tool()
async def search(query: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Search tool returning quotes in ChatGPT-expected MCP format.

    Returns a list of search results with basic information. 
    Use the fetch tool to get complete document content.

    Args:
            query: Search query string. Natural language queries work best for semantic search.

    Returns:
            Dictionary with 'results' key containing list of matching documents.
            Each result includes id, title, text snippet, and optional URL.
    """

    if not query or not query.strip():
        return {"results": []}

    results = []
    # Do fuzzy search through quotes for any matches
    query_lower = query.lower()
    for quote in quotes:
        # Check if query appears in quote or author (case-insensitive)
        if (query_lower in quote["quote"].lower() or 
            query_lower in quote["author"].lower()):
            
            results.append({
                "id": quote["id"],
                "title": f"Quote by {quote['author']}",
                "text": quote["quote"],
                "url": f"https://example.com/{quote['id']}"
            })

    return {"results": results}

# -------------------------------
#           FETCH tool
# -------------------------------
@mcp.tool()
async def fetch(id: str) -> Dict[str, Any]:
    """
    Fetch tool returning a single document in ChatGPT-expected MCP format.

    Use this after finding relevant documents with the search tool to get complete information for analysis and proper citation.

    Args:
        id: Document ID string.

    Returns:
        Complete document with id, title, full text content,
        optional URL, and metadata

    Raises:
        ValueError: If the specified ID is not found
    """
    
    # Find quote with matching ID
    matching_quote = None
    for quote in quotes:
        if quote["id"] == id:
            matching_quote = quote
            break
            
    if not matching_quote:
        raise ValueError(f"Quote with ID {id} not found")
        
    # Return quote in expected format
    result = {
        "id": matching_quote["id"],
        "title": f"Quote by {matching_quote['author']}", 
        "text": f"Complete quote: {matching_quote['quote']}",
        "url": f"https://example.com/{matching_quote['id']}",
        "metadata": {"author": matching_quote['author']}
    }

    return result

# Health probe (must be registered before creating the ASGI app)
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    print("Health check")
    return PlainTextResponse("OK")    

# Expose ASGI app for Gunicorn/Uvicorn (Azure App Service)
app = mcp.http_app()