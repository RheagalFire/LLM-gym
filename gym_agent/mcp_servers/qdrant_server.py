from mcp.server.fastmcp import FastMCP
from gym_agent.clients.qdrant_client import qdrant_client
import asyncio

mcp = FastMCP("Qdrant MCP Server")


@mcp.tool("search")
async def search(collection_name: str, query_vector: list, limit: int = 5):
    """
    Search for similar vectors in the collection

    Args:
        collection_name: The name of the collection to search in
        query_vector: The query vector
        limit: The maximum number of results to return

    Returns:
        The search results
    """
    try:
        results = qdrant_client.search(
            collection_name=collection_name, query_vector=query_vector, limit=limit
        )
        return results
    except Exception as e:
        print(f"Error searching Qdrant: {str(e)}")
        return []


if __name__ == "__main__":
    asyncio.run(mcp.run())
