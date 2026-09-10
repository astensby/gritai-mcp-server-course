from typing import Any, Dict, List

from fastmcp import FastMCP

# Plain import, not a relative one: this file is run as a script
# (fastmcp dev / uv run / Claude Desktop), where there is no parent package.
from rag_retrieval_tools import answer_query

mcp = FastMCP("local-rag-server")


def format_rag_results(results: List[Dict[str, Any]]) -> str:
    """Formats the list of dictionaries from answer_query into a readable string."""
    if not results:
        return "No relevant information found."

    formatted_output = "Found relevant information:\n\n"
    for i, result in enumerate(results):
        chunk = result.get("chunk", {})
        score = result.get("score", 0.0)
        text = chunk.get("content", "N/A")
        filename = chunk.get("filename", "N/A")
        chunk_id = chunk.get("chunk_id", "N/A")
        preview_text = (text[:250] + "...") if len(text) > 250 else text

        formatted_output += f"Result {i + 1} (Score: {score:.4f}, Source: {filename}, ID: {chunk_id}):\n"
        formatted_output += f'"{preview_text}"\n\n'

    return formatted_output.strip()


@mcp.tool()
def search_local_rag_knowledge_base(query: str) -> str:
    """Search the knowledge base

    Args:
        query: The query to search the knowledge base with
    """
    try:
        retrieved_results = answer_query(query, top_n=3)
        return format_rag_results(retrieved_results)
    except Exception as e:
        return f"An error occurred while searching the knowledge base: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
