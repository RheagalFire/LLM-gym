from mcp.server.fastmcp import FastMCP
from gym_db.db_funcs import DbOps
from gym_reader.clients.prisma_client import prisma_singleton
import asyncio

mcp = FastMCP("Postgres MCP Client")


# Initialize client and dbops in an async function
async def initialize_db():
    client = await prisma_singleton.get_client()
    return DbOps(client)


# Create a global variable for dbops
dbops = None


@mcp.tool("get_unindexed_files")
async def get_unindexed_files():
    global dbops
    # Initialize dbops if not already initialized
    if dbops is None:
        dbops = await initialize_db()

    # Get unindexed files
    files = await dbops.get_documents_to_index()
    return files


@mcp.tool("get_indexed_files")
async def get_indexed_files():
    global dbops
    # Initialize dbops if not already initialized
    if dbops is None:
        dbops = await initialize_db()

    # Get indexed files
    files = await dbops.get_indexed_documents()
    return files


if __name__ == "__main__":
    asyncio.run(mcp.run())
