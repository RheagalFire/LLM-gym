import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union, Annotated
from pydantic import BaseModel, Field
import logging

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

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
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

        # Add nodes - using different names for nodes to avoid collision with state fields
        builder.add_node("understand_query", self._query_understanding)
        builder.add_node("select_tool", self._tool_selection)
        builder.add_node("execute_tool", self._tool_execution)
        builder.add_node("generate_response", self._response_generation)

        # Add edges
        builder.add_edge("understand_query", "select_tool")
        builder.add_edge("select_tool", "execute_tool")
        builder.add_edge("execute_tool", "generate_response")
        builder.add_edge("generate_response", END)

        # Set the entry point
        builder.set_entry_point("understand_query")

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
        
        Respond with a JSON object containing the following fields:
        - "intent": A string describing the intent of the query
        - "rephrased_query": A string with the rephrased query
        - "required_tools": An array of strings with the required tools (from the list above)
        """

        prompt = f"""
        User Query: {state.query}
        
        Conversation History: {state.conversation_history}
        
        Analyze the query and provide:
        1. The intent of the query
        2. A rephrased version of the query that would be more effective for search
        3. The tools required to answer the query
        
        Format your response as JSON.
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
        
        Respond with a JSON object containing the following fields:
        - "selected_tool": A string with the selected tool (from the list above)
        - "tool_params": An object with the parameters for the selected tool
        - "reasoning": A string explaining why you selected this tool
        """

        prompt = f"""
        User Query: {state.query}
        
        Query Understanding:
        - Rephrased Query: {state.query_understanding.rephrased_query}
        - Intent: {state.query_understanding.intent}
        - Required Tools: {[tool.value for tool in state.query_understanding.required_tools]}
        
        Select the most appropriate tool and provide the necessary parameters.
        
        Format your response as JSON.
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
        
        logger.info(f"Executing tool: {selected_tool.value}")
        logger.debug(f"Tool parameters: {json.dumps(tool_params, default=str)}")

        # Execute the tool
        if selected_tool == ToolType.QDRANT_SEARCH:
            logger.info("Using Qdrant search")
            query = tool_params.get("query", state.query_understanding.rephrased_query)
            collection_name = tool_params.get("collection_name", "LLM-gym")
            limit = tool_params.get("limit", 5)
            
            logger.debug(f"Qdrant search parameters - query: '{query}', collection: '{collection_name}', limit: {limit}")
            
            # Use direct client instead of MCP to avoid async issues
            try:
                tool_result = SearchTools.search_qdrant(
                    query=query,
                    collection_name=collection_name,
                    limit=limit
                )
                logger.info(f"Qdrant search completed with {len(tool_result.raw_results)} results")
            except Exception as e:
                logger.error(f"Error during Qdrant search: {str(e)}")
                tool_result = ToolExecutionResult(
                    tool_type=ToolType.QDRANT_SEARCH,
                    raw_results=[],
                    processed_results=f"Qdrant search failed with error: {str(e)}. Using model's knowledge to answer the query.",
                    error=str(e)
                )

        elif selected_tool == ToolType.MEILISEARCH:
            logger.info("Using MeiliSearch")
            query = tool_params.get("query", state.query_understanding.rephrased_query)
            index_name = tool_params.get("index_name", "LLM-gym")
            limit = tool_params.get("limit", 5)
            
            logger.debug(f"MeiliSearch parameters - query: '{query}', index: '{index_name}', limit: {limit}")
            
            # Use direct client instead of MCP to avoid async issues
            try:
                tool_result = SearchTools.search_meilisearch(
                    query=query,
                    index_name=index_name,
                    limit=limit
                )
                logger.info(f"MeiliSearch completed with {len(tool_result.raw_results)} results")
            except Exception as e:
                logger.error(f"Error during MeiliSearch: {str(e)}")
                tool_result = ToolExecutionResult(
                    tool_type=ToolType.MEILISEARCH,
                    raw_results=[],
                    processed_results=f"MeiliSearch failed with error: {str(e)}. Using model's knowledge to answer the query.",
                    error=str(e)
                )

        elif selected_tool == ToolType.WEB_SEARCH:
            logger.info("Using Web Search (Tavily)")
            query = tool_params.get("query", state.query_understanding.rephrased_query)
            search_depth = "basic"
            
            logger.info(f"Web search parameters - query: '{query}', depth: '{search_depth}'")
            
            try:
                tool_result = SearchTools.search_web(
                    query=query,
                    search_depth=search_depth
                )
                logger.info(f"Web search completed with {len(tool_result.raw_results)} results")
                
                # Check if we got any results
                if not tool_result.raw_results:
                    logger.warning("Web search returned no results")
                    # If web search failed or returned no results, add a note to the processed results
                    tool_result = ToolExecutionResult(
                        tool_type=ToolType.WEB_SEARCH,
                        raw_results=[],
                        processed_results="Web search was attempted but returned no results. Using model's knowledge to answer the query.",
                        error="No web search results found."
                    )
            except Exception as e:
                logger.error(f"Error during web search: {str(e)}")
                # Handle any exceptions during web search
                tool_result = ToolExecutionResult(
                    tool_type=ToolType.WEB_SEARCH,
                    raw_results=[],
                    processed_results=f"Web search failed with error: {str(e)}. Using model's knowledge to answer the query.",
                    error=str(e)
                )

        else:  # ToolType.NONE
            logger.info("No tool execution required")
            tool_result = ToolExecutionResult(
                tool_type=ToolType.NONE,
                raw_results=[],
                processed_results="No tool execution required."
            )

        logger.debug(f"Tool execution result: {tool_result.tool_type.value}, error: {tool_result.error or 'None'}")
        
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
        
        Respond with a JSON object containing the following fields:
        - "answer": A string with the comprehensive answer to the user's query
        - "sources": An array of objects, each with "title" and "url" fields
        - "confidence": A number between 0 and 1 indicating your confidence in the answer
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
        
        Format your response as JSON.
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
        self, query: str, conversation_history: Optional[List[Dict[str, str]]] = None, debug: bool = False
    ) -> str:
        """
        Run the agent on the given query

        Args:
            query: The query to run the agent on
            conversation_history: The conversation history
            debug: Whether to run in debug mode (prints additional information)

        Returns:
            The agent's response
        """
        logger.info(f"Running agent with query: '{query}'")
        if debug:
            # Set logging level to DEBUG for this run
            logging.getLogger('gym_agent').setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")
        
        if conversation_history is None:
            conversation_history = []
        
        logger.debug(f"Conversation history has {len(conversation_history)} messages")

        # Create the initial state
        initial_state = AgentState(
            query=query, conversation_history=conversation_history
        )
        
        logger.info("Invoking graph")
        try:
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            logger.info("Graph execution completed successfully")
            
            if debug:
                # Log the final state structure
                if isinstance(final_state, dict):
                    logger.debug(f"Final state keys: {list(final_state.keys())}")
                else:
                    logger.debug(f"Final state type: {type(final_state)}")
            
            # Return the response
            # In LangGraph, the final state is returned as a dictionary
            if isinstance(final_state, dict) and "response" in final_state:
                if final_state["response"]:
                    logger.info("Successfully extracted response from final state")
                    return final_state["response"].answer
                else:
                    logger.warning("Response object is None in final state")
            else:
                logger.warning(f"No 'response' key in final state or final state is not a dictionary")
        
        except Exception as e:
            logger.error(f"Error during graph execution: {str(e)}")
            logger.exception("Detailed traceback:")
        
        # Fallback response if we can't get the proper response
        logger.warning("Using fallback response")
        return "I couldn't generate a response to your query."


# Example usage
if __name__ == "__main__":
    agent = GraphAgent()
    response = agent.run("What are the key concepts in LLM inference?")
    print(response)
