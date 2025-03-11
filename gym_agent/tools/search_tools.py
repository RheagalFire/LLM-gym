import asyncio
from typing import Dict, Any, List, Optional
from gym_agent.clients.qdrant_client import qdrant_client
from gym_agent.clients.meilisearch_client import meilisearch_client
from gym_agent.clients.tavily_client import tavily_client
from gym_agent.clients.openai_client import openai_client
from gym_agent.clients.mcp_client import QdrantMCPClient, MeiliSearchMCPClient
from gym_agent.schemas.agent_schemas import ToolExecutionResult, ToolType
import json


class SearchTools:
    """
    Tools for searching various data sources
    """

    @staticmethod
    def get_embedding(text: str) -> List[float]:
        """
        Get an embedding for the given text using OpenAI

        Args:
            text: The text to embed

        Returns:
            The embedding vector
        """
        response = openai_client.embeddings.create(
            model="text-embedding-3-small", input=text, dimensions=1536
        )
        return response.data[0].embedding

    @staticmethod
    def search_qdrant(
        query: str, collection_name: str, limit: int = 5
    ) -> ToolExecutionResult:
        """
        Search Qdrant for the given query

        Args:
            query: The search query
            collection_name: The name of the collection to search in
            limit: The maximum number of results to return

        Returns:
            The search results
        """
        try:
            # Get the embedding for the query
            query_vector = SearchTools.get_embedding(query)

            # Search Qdrant
            results = qdrant_client.search(
                collection_name=collection_name, query_vector=query_vector, limit=limit
            )

            # Process the results
            processed_results = "Search Results:\n\n"
            for i, result in enumerate(results):
                processed_results += f"{i+1}. Score: {result.score:.4f}\n"
                for key, value in result.payload.items():
                    if isinstance(value, str) and len(value) > 300:
                        value = value[:300] + "..."
                    processed_results += f"   {key}: {value}\n"
                processed_results += "\n"

            return ToolExecutionResult(
                tool_type=ToolType.QDRANT_SEARCH,
                raw_results=[
                    dict(id=r.id, score=r.score, payload=r.payload) for r in results
                ],
                processed_results=processed_results,
            )
        except Exception as e:
            error_message = f"Error searching Qdrant: {str(e)}"
            return ToolExecutionResult(
                tool_type=ToolType.QDRANT_SEARCH,
                raw_results=[],
                processed_results="No results found due to an error.",
                error=error_message,
            )

    @staticmethod
    def search_meilisearch(
        query: str, index_name: str, limit: int = 5
    ) -> ToolExecutionResult:
        """
        Search MeiliSearch for the given query

        Args:
            query: The search query
            index_name: The name of the index to search in
            limit: The maximum number of results to return

        Returns:
            The search results
        """
        try:
            # Search MeiliSearch
            search_settings = {
                "limit": limit,
                "attributesToHighlight": ["*"],
                "highlightPreTag": "<em>",
                "highlightPostTag": "</em>",
            }

            results = meilisearch_client.index(index_name).search(
                query, search_settings
            )

            # Process the results
            processed_results = "Search Results:\n\n"
            for i, hit in enumerate(results["hits"]):
                processed_results += f"{i+1}. "
                if "parent_title" in hit:
                    processed_results += f"Title: {hit['parent_title']}\n"
                if "parent_link" in hit:
                    processed_results += f"   URL: {hit['parent_link']}\n"
                if "parent_summary" in hit:
                    summary = hit["parent_summary"]
                    if len(summary) > 300:
                        summary = summary[:300] + "..."
                    processed_results += f"   Summary: {summary}\n"
                if "parent_keywords" in hit and hit["parent_keywords"]:
                    processed_results += (
                        f"   Keywords: {', '.join(hit['parent_keywords'][:5])}\n"
                    )
                processed_results += "\n"

            return ToolExecutionResult(
                tool_type=ToolType.MEILISEARCH,
                raw_results=results["hits"],
                processed_results=processed_results,
            )
        except Exception as e:
            error_message = f"Error searching MeiliSearch: {str(e)}"
            return ToolExecutionResult(
                tool_type=ToolType.MEILISEARCH,
                raw_results=[],
                processed_results="No results found due to an error.",
                error=error_message,
            )

    @staticmethod
    def search_web(query: str, search_depth: str = "basic") -> ToolExecutionResult:
        """
        Search the web for the given query using Tavily

        Args:
            query: The search query
            search_depth: The search depth (basic or comprehensive)

        Returns:
            The search results
        """
        try:
            # Search the web
            results = tavily_client.search(query, search_depth)

            # Process the results
            processed_results = "Web Search Results:\n\n"
            for i, result in enumerate(results.get("results", [])):
                processed_results += (
                    f"{i+1}. Title: {result.get('title', 'No title')}\n"
                )
                processed_results += f"   URL: {result.get('url', 'No URL')}\n"

                content = result.get("content", "No content")
                if len(content) > 300:
                    content = content[:300] + "..."
                processed_results += f"   Content: {content}\n\n"

            return ToolExecutionResult(
                tool_type=ToolType.WEB_SEARCH,
                raw_results=results.get("results", []),
                processed_results=processed_results,
            )
        except Exception as e:
            error_message = f"Error searching the web: {str(e)}"
            return ToolExecutionResult(
                tool_type=ToolType.WEB_SEARCH,
                raw_results=[],
                processed_results="No results found due to an error.",
                error=error_message,
            )

    @staticmethod
    async def search_qdrant_mcp(
        query: str, collection_name: str, limit: int = 5
    ) -> ToolExecutionResult:
        """
        Search Qdrant for the given query using MCP

        Args:
            query: The search query
            collection_name: The name of the collection to search in
            limit: The maximum number of results to return

        Returns:
            The search results
        """
        try:
            # Get the embedding for the query
            query_vector = SearchTools.get_embedding(query)

            # Create MCP client
            client = QdrantMCPClient()

            # Search Qdrant
            results = await client.search(
                collection_name=collection_name, query_vector=query_vector, limit=limit
            )

            # Process the results
            processed_results = "Search Results:\n\n"
            for i, result in enumerate(results):
                processed_results += f"{i+1}. Score: {result.get('score', 0):.4f}\n"
                for key, value in result.get("payload", {}).items():
                    if isinstance(value, str) and len(value) > 300:
                        value = value[:300] + "..."
                    processed_results += f"   {key}: {value}\n"
                processed_results += "\n"

            return ToolExecutionResult(
                tool_type=ToolType.QDRANT_SEARCH,
                raw_results=results,
                processed_results=processed_results,
            )
        except Exception as e:
            error_message = f"Error searching Qdrant via MCP: {str(e)}"
            return ToolExecutionResult(
                tool_type=ToolType.QDRANT_SEARCH,
                raw_results=[],
                processed_results="No results found due to an error.",
                error=error_message,
            )

    @staticmethod
    async def search_meilisearch_mcp(
        query: str, index_name: str, limit: int = 5
    ) -> ToolExecutionResult:
        """
        Search MeiliSearch for the given query using MCP

        Args:
            query: The search query
            index_name: The name of the index to search in
            limit: The maximum number of results to return

        Returns:
            The search results
        """
        try:
            # Create MCP client
            client = MeiliSearchMCPClient()

            # Search MeiliSearch
            results = await client.search(
                index_name=index_name, query=query, limit=limit
            )

            # Process the results
            processed_results = "Search Results:\n\n"
            for i, hit in enumerate(results.get("hits", [])):
                processed_results += f"{i+1}. "
                if "parent_title" in hit:
                    processed_results += f"Title: {hit['parent_title']}\n"
                if "parent_link" in hit:
                    processed_results += f"   URL: {hit['parent_link']}\n"
                if "parent_summary" in hit:
                    summary = hit["parent_summary"]
                    if len(summary) > 300:
                        summary = summary[:300] + "..."
                    processed_results += f"   Summary: {summary}\n"
                if "parent_keywords" in hit and hit["parent_keywords"]:
                    processed_results += (
                        f"   Keywords: {', '.join(hit['parent_keywords'][:5])}\n"
                    )
                processed_results += "\n"

            return ToolExecutionResult(
                tool_type=ToolType.MEILISEARCH,
                raw_results=results.get("hits", []),
                processed_results=processed_results,
            )
        except Exception as e:
            error_message = f"Error searching MeiliSearch via MCP: {str(e)}"
            return ToolExecutionResult(
                tool_type=ToolType.MEILISEARCH,
                raw_results=[],
                processed_results="No results found due to an error.",
                error=error_message,
            )
