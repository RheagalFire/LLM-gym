import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union, Annotated
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import AnyMessage

from gym_agent.clients.openai_client import get_structured_output, get_completion
from gym_agent.schemas.agent_schemas import (
    AgentState,
    QueryUnderstanding,
    ToolSelection,
    ToolExecutionResult,
    AgentResponse,
    ToolType,
)
from gym_agent.tools.search_tools import SearchTools
from gym_agent.settings import get_settings

settings = get_settings()


class GraphAgent:
    """
    A graph-based agent using LangGraph
    """

    def __init__(self):
        """
        Initialize the graph agent
        """
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build the graph for the agent

        Returns:
            The state graph
        """
        # Create the graph
        builder = StateGraph(AgentState)

        # Add nodes
        builder.add_node("query_understanding", self._query_understanding)
        builder.add_node("tool_selection", self._tool_selection)
        builder.add_node("tool_execution", self._tool_execution)
        builder.add_node("response_generation", self._response_generation)

        # Add edges
        builder.add_edge("query_understanding", "tool_selection")
        builder.add_edge("tool_selection", "tool_execution")
        builder.add_edge("tool_execution", "response_generation")
        builder.add_edge("response_generation", END)

        # Set the entry point
        builder.set_entry_point("query_understanding")

        # Compile the graph
        return builder.compile()

    def _query_understanding(self, state: AgentState) -> AgentState:
        """
        Understand the query and determine the required tools

        Args:
            state: The current state

        Returns:
            The updated state
        """
        system_message = """
        You are an AI assistant that helps users find information. Your task is to understand the user's query and determine the best approach to answer it.
        
        1. Analyze the query to understand its intent
        2. Rephrase the query to make it more effective for search
        3. Determine which tools are required to answer the query
        
        Available tools:
        - qdrant_search: For semantic vector search
        - meilisearch: For keyword-based search
        - web_search: For searching the web for up-to-date information
        - none: If no tools are required to answer the query
        """

        prompt = f"""
        User Query: {state.query}
        
        Conversation History: {state.conversation_history}
        
        Analyze the query and provide:
        1. The intent of the query
        2. A rephrased version of the query that would be more effective for search
        3. The tools required to answer the query
        """

        # Get structured output
        result = get_structured_output(
            prompt=prompt,
            system_message=system_message,
            response_format={"type": "json_object"},
            model=settings.DEFAULT_MODEL,
        )

        # Parse the result
        result_dict = json.loads(result)

        # Create QueryUnderstanding object
        query_understanding = QueryUnderstanding(
            query=state.query,
            rephrased_query=result_dict.get("rephrased_query", state.query),
            intent=result_dict.get("intent", ""),
            required_tools=[
                ToolType(tool)
                for tool in result_dict.get("required_tools", [ToolType.NONE])
            ],
        )

        # Update the state
        return AgentState(
            query=state.query,
            query_understanding=query_understanding,
            conversation_history=state.conversation_history,
        )

    def _tool_selection(self, state: AgentState) -> AgentState:
        """
        Select the appropriate tool based on the query understanding

        Args:
            state: The current state

        Returns:
            The updated state
        """
        system_message = """
        You are an AI assistant that helps users find information. Your task is to select the most appropriate tool to answer the user's query.
        
        Available tools:
        - qdrant_search: For semantic vector search
        - meilisearch: For keyword-based search
        - web_search: For searching the web for up-to-date information
        - none: If no tools are required to answer the query
        
        For each tool, you need to provide the appropriate parameters:
        - qdrant_search: collection_name, query, limit
        - meilisearch: index_name, query, limit
        - web_search: query, search_depth (basic or comprehensive)
        - none: No parameters required
        """

        prompt = f"""
        User Query: {state.query}
        
        Query Understanding:
        - Rephrased Query: {state.query_understanding.rephrased_query}
        - Intent: {state.query_understanding.intent}
        - Required Tools: {[tool.value for tool in state.query_understanding.required_tools]}
        
        Select the most appropriate tool and provide the necessary parameters.
        """

        # Get structured output
        result = get_structured_output(
            prompt=prompt,
            system_message=system_message,
            response_format={"type": "json_object"},
            model=settings.DEFAULT_MODEL,
        )

        # Parse the result
        result_dict = json.loads(result)

        # Create ToolSelection object
        tool_selection = ToolSelection(
            selected_tool=ToolType(result_dict.get("selected_tool", ToolType.NONE)),
            tool_params=result_dict.get("tool_params", {}),
            reasoning=result_dict.get("reasoning", ""),
        )

        # Update the state
        return AgentState(
            query=state.query,
            query_understanding=state.query_understanding,
            tool_selection=tool_selection,
            conversation_history=state.conversation_history,
        )

    def _tool_execution(self, state: AgentState) -> AgentState:
        """
        Execute the selected tool

        Args:
            state: The current state

        Returns:
            The updated state
        """
        # Get the selected tool and parameters
        selected_tool = state.tool_selection.selected_tool
        tool_params = state.tool_selection.tool_params

        # Execute the tool
        if selected_tool == ToolType.QDRANT_SEARCH:
            # Use MCP if available, otherwise use direct client
            try:
                # Run the async function in a synchronous context
                tool_result = asyncio.run(
                    SearchTools.search_qdrant_mcp(
                        query=tool_params.get(
                            "query", state.query_understanding.rephrased_query
                        ),
                        collection_name=tool_params.get("collection_name", "LLM-gym"),
                        limit=tool_params.get("limit", 5),
                    )
                )
            except Exception as e:
                # Fallback to direct client
                tool_result = SearchTools.search_qdrant(
                    query=tool_params.get(
                        "query", state.query_understanding.rephrased_query
                    ),
                    collection_name=tool_params.get("collection_name", "LLM-gym"),
                    limit=tool_params.get("limit", 5),
                )

        elif selected_tool == ToolType.MEILISEARCH:
            # Use MCP if available, otherwise use direct client
            try:
                # Run the async function in a synchronous context
                tool_result = asyncio.run(
                    SearchTools.search_meilisearch_mcp(
                        query=tool_params.get(
                            "query", state.query_understanding.rephrased_query
                        ),
                        index_name=tool_params.get("index_name", "LLM-gym"),
                        limit=tool_params.get("limit", 5),
                    )
                )
            except Exception as e:
                # Fallback to direct client
                tool_result = SearchTools.search_meilisearch(
                    query=tool_params.get(
                        "query", state.query_understanding.rephrased_query
                    ),
                    index_name=tool_params.get("index_name", "LLM-gym"),
                    limit=tool_params.get("limit", 5),
                )

        elif selected_tool == ToolType.WEB_SEARCH:
            tool_result = SearchTools.search_web(
                query=tool_params.get(
                    "query", state.query_understanding.rephrased_query
                ),
                search_depth=tool_params.get("search_depth", "basic"),
            )

        else:  # ToolType.NONE
            tool_result = ToolExecutionResult(
                tool_type=ToolType.NONE,
                raw_results=[],
                processed_results="No tool execution required.",
            )

        # Update the state
        return AgentState(
            query=state.query,
            query_understanding=state.query_understanding,
            tool_selection=state.tool_selection,
            tool_execution_result=tool_result,
            conversation_history=state.conversation_history,
        )

    def _response_generation(self, state: AgentState) -> AgentState:
        """
        Generate a response based on the tool execution results

        Args:
            state: The current state

        Returns:
            The updated state
        """
        system_message = """
        You are an AI assistant that helps users find information. Your task is to generate a helpful response based on the search results.
        
        1. Analyze the search results
        2. Extract the most relevant information
        3. Provide a comprehensive answer to the user's query
        4. Include sources for the information
        5. Indicate your confidence in the answer (0-1)
        """

        prompt = f"""
        User Query: {state.query}
        
        Query Understanding:
        - Rephrased Query: {state.query_understanding.rephrased_query}
        - Intent: {state.query_understanding.intent}
        
        Tool Execution Results:
        - Tool: {state.tool_execution_result.tool_type.value}
        - Results: {state.tool_execution_result.processed_results}
        
        Generate a comprehensive response to the user's query based on the search results.
        """

        # Get structured output
        result = get_structured_output(
            prompt=prompt,
            system_message=system_message,
            response_format={"type": "json_object"},
            model=settings.DEFAULT_MODEL,
        )

        # Parse the result
        result_dict = json.loads(result)

        # Create AgentResponse object
        response = AgentResponse(
            answer=result_dict.get(
                "answer", "I couldn't find an answer to your query."
            ),
            sources=result_dict.get("sources", []),
            confidence=result_dict.get("confidence", 0.0),
        )

        # Update conversation history
        conversation_history = state.conversation_history.copy()
        conversation_history.append({"role": "user", "content": state.query})
        conversation_history.append({"role": "assistant", "content": response.answer})

        # Update the state
        return AgentState(
            query=state.query,
            query_understanding=state.query_understanding,
            tool_selection=state.tool_selection,
            tool_execution_result=state.tool_execution_result,
            response=response,
            conversation_history=conversation_history,
        )

    def run(
        self, query: str, conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Run the agent on the given query

        Args:
            query: The query to run the agent on
            conversation_history: The conversation history

        Returns:
            The agent's response
        """
        if conversation_history is None:
            conversation_history = []

        # Create the initial state
        initial_state = AgentState(
            query=query, conversation_history=conversation_history
        )

        # Run the graph
        final_state = self.graph.invoke(initial_state)

        # Return the response
        if final_state.response:
            return final_state.response.answer
        else:
            return "I couldn't generate a response to your query."


# Example usage
if __name__ == "__main__":
    agent = GraphAgent()
    response = agent.run("What are the key concepts in LLM inference?")
    print(response)
