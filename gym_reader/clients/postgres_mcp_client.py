import asyncio
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class PostgresMCPClient:
    """
    Client for interacting with the Postgres MCP server
    """

    def __init__(self, server_url: str = "http://localhost:8000"):
        """
        Initialize the Postgres MCP client

        Args:
            server_url: URL of the Postgres MCP server
        """
        self.server_url = server_url
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
                args=["-m", "gym_reader.fastmcp_servers.postgres_server"],
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

    async def get_unindexed_files(self) -> List[Dict[str, Any]]:
        """
        Fetch unindexed files from the Postgres MCP server

        Returns:
            List of document dictionaries that need to be indexed
        """
        session = await self.connect()

        try:
            # Call the tool directly
            result = await session.call_tool("get_unindexed_files", {})

            # Return the content from the result
            return result.content
        except Exception as e:
            print(f"Error calling get_unindexed_files: {str(e)}")
            # Return empty list on error
            return []

    async def get_indexed_files(self) -> List[Dict[str, Any]]:
        """
        Fetch indexed files from the Postgres MCP server
        """
        session = await self.connect()

        try:
            # Call the tool directly
            result = await session.call_tool("get_indexed_files", {})

            # Return the content from the result
            return result.content
        except Exception as e:
            print(f"Error calling get_indexed_files: {str(e)}")

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


# Singleton instance for easy access
postgres_mcp_singleton = None


async def get_client(server_url: str = "http://localhost:8000") -> PostgresMCPClient:
    """
    Get or create a PostgresMCPClient instance

    Args:
        server_url: URL of the Postgres MCP server

    Returns:
        PostgresMCPClient instance
    """
    global postgres_mcp_singleton
    if postgres_mcp_singleton is None:
        postgres_mcp_singleton = PostgresMCPClient(server_url)
    elif server_url != "http://localhost:8000":
        # Close the existing client if the URL changes
        if postgres_mcp_singleton.session is not None:
            await postgres_mcp_singleton.close()
        postgres_mcp_singleton = PostgresMCPClient(server_url)
    return postgres_mcp_singleton
