from mcp.server.fastmcp import FastMCP
from gym_agent.clients.meilisearch_client import meilisearch_client
import asyncio

mcp = FastMCP("MeiliSearch MCP Server")


@mcp.tool("search")
async def search(index_name: str, query: str, limit: int = 5):
    """
    Search for documents in the index

    Args:
        index_name: The name of the index to search in
        query: The search query
        limit: The maximum number of results to return

    Returns:
        The search results
    """
    try:
        search_settings = {
            "limit": limit,
            "attributesToHighlight": ["*"],
            "highlightPreTag": "<em>",
            "highlightPostTag": "</em>",
        }

        results = meilisearch_client.index(index_name).search(query, search_settings)
        return results
    except Exception as e:
        print(f"Error searching MeiliSearch: {str(e)}")
        return {"hits": []}


if __name__ == "__main__":
    asyncio.run(mcp.run())
