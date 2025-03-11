import asyncio
from typing import Optional, Dict, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPClient:
    """
    Client for interacting with MCP servers
    """

    def __init__(self, server_module: str):
        """
        Initialize the MCP client

        Args:
            server_module: The Python module path to the MCP server
        """
        self.server_module = server_module
        self.session = None
        self.exit_stack = None
        self.stdio = None
        self.write = None

    async def connect(self):
        """
        Connect to the MCP server
        """
        if self.session is None:
            # Create exit stack for resource management
            self.exit_stack = AsyncExitStack()

            # For HTTP-based connection, we would use different transport
            # But for now, we'll use stdio for simplicity
            server_params = StdioServerParameters(
                command="python",
                args=["-m", self.server_module],
                env=None,
            )

            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )

            # Initialize the session
            await self.session.initialize()

        return self.session

    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the MCP server

        Args:
            tool_name: The name of the tool to call
            params: The parameters to pass to the tool

        Returns:
            The result of the tool call
        """
        session = await self.connect()

        try:
            # Call the tool directly
            result = await session.call_tool(tool_name, params)

            # Return the content from the result
            return result.content
        except Exception as e:
            logger.error(f"Error calling {tool_name}: {str(e)}")
            # Return empty dict on error
            return {}

    async def close(self):
        """
        Close the client connection
        """
        if self.exit_stack:
            await self.exit_stack.aclose()
            self.session = None
            self.stdio = None
            self.write = None
            self.exit_stack = None


class QdrantMCPClient(MCPClient):
    """
    MCP client for Qdrant
    """

    def __init__(self):
        super().__init__("gym_agent.mcp_servers.qdrant_server")

    async def search(self, collection_name: str, query_vector: list, limit: int = 5):
        """
        Search for similar vectors in the collection

        Args:
            collection_name: The name of the collection to search in
            query_vector: The query vector
            limit: The maximum number of results to return

        Returns:
            The search results
        """
        return await self.call_tool(
            "search",
            {
                "collection_name": collection_name,
                "query_vector": query_vector,
                "limit": limit,
            },
        )


class MeiliSearchMCPClient(MCPClient):
    """
    MCP client for MeiliSearch
    """

    def __init__(self):
        super().__init__("gym_agent.mcp_servers.meilisearch_server")

    async def search(self, index_name: str, query: str, limit: int = 5):
        """
        Search for documents in the index

        Args:
            index_name: The name of the index to search in
            query: The search query
            limit: The maximum number of results to return

        Returns:
            The search results
        """
        return await self.call_tool(
            "search", {"index_name": index_name, "query": query, "limit": limit}
        )
