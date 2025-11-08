import os
import json
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import AzureError

load_dotenv()

mcp = FastMCP("azure-ai-search", dependencies=["azure-search-documents", "azure-identity"])

@mcp.tool()
def search_azure_index(query: str, top_k: int = 5) -> str:
    """Search the Azure AI Search index for the most relevant information.

    Args:
        query: The search query text
        top_k: Number of top results to return (default: 5)
    """
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_index = os.environ.get("AZURE_SEARCH_INDEX")
    search_key = os.environ.get("AZURE_SEARCH_KEY")

    if not search_endpoint:
        return "Error: AZURE_SEARCH_ENDPOINT environment variable not set."
    if not search_index:
        return "Error: AZURE_SEARCH_INDEX environment variable not set."

    try:
        # Flexible authentication: API key first, fall back to DefaultAzureCredential
        if search_key:
            credential = AzureKeyCredential(search_key)
            auth_method = "API Key"
        else:
            credential = DefaultAzureCredential()
            auth_method = "DefaultAzureCredential"

        # Create search client
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=search_index,
            credential=credential
        )

        # Perform search
        results = search_client.search(
            search_text=query,
            top=top_k,
            include_total_count=True
        )

        # Format results
        formatted_results = []
        result_count = 0

        for result in results:
            result_count += 1
            score = result.get('@search.score', 'N/A')

            # Extract all fields except internal Azure fields
            content_fields = {k: v for k, v in result.items() if not k.startswith('@')}
            content_str = json.dumps(content_fields, indent=2)

            formatted_results.append(
                f"Result {result_count} (Score: {score}):\n{content_str}\n---"
            )

        if not formatted_results:
            return f"No relevant information found in index '{search_index}' for query: '{query}'"

        header = f"Found {result_count} results using {auth_method}:\n\n"
        return header + "\n".join(formatted_results)

    except AzureError as e:
        return f"Error calling Azure AI Search API: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    required_vars = ["AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_INDEX"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them before running the server.")
        print("\nOptional: Set AZURE_SEARCH_KEY for API key auth, or configure Azure CLI for DefaultAzureCredential.")

    mcp.run(transport='stdio')
