from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union


class ToolType(str, Enum):
    QDRANT_SEARCH = "qdrant_search"
    MEILISEARCH = "meilisearch"
    WEB_SEARCH = "web_search"
    NONE = "none"


class QueryUnderstanding(BaseModel):
    """Schema for the query understanding node output"""

    query: str = Field(..., description="The original query from the user")
    rephrased_query: str = Field(
        ..., description="The rephrased query for better search results"
    )
    intent: str = Field(..., description="The intent of the query")
    required_tools: List[ToolType] = Field(
        ..., description="The tools required to answer the query"
    )


class ToolSelection(BaseModel):
    """Schema for the tool selection node output"""

    selected_tool: ToolType = Field(..., description="The selected tool to use")
    tool_params: Dict[str, Any] = Field(
        ..., description="The parameters to pass to the tool"
    )
    reasoning: str = Field(..., description="The reasoning for selecting this tool")


class QdrantSearchResult(BaseModel):
    """Schema for Qdrant search results"""

    id: str = Field(..., description="The ID of the document")
    score: float = Field(..., description="The similarity score")
    payload: Dict[str, Any] = Field(..., description="The document payload")


class MeiliSearchResult(BaseModel):
    """Schema for MeiliSearch results"""

    id: str = Field(..., description="The ID of the document")
    title: str = Field(..., description="The title of the document")
    content: str = Field(..., description="The content of the document")
    url: Optional[str] = Field(None, description="The URL of the document")
    highlights: Dict[str, List[str]] = Field(
        ..., description="The highlighted parts of the document"
    )


class WebSearchResult(BaseModel):
    """Schema for web search results"""

    title: str = Field(..., description="The title of the webpage")
    content: str = Field(..., description="The content of the webpage")
    url: str = Field(..., description="The URL of the webpage")


class ToolExecutionResult(BaseModel):
    """Schema for the tool execution node output"""

    tool_type: ToolType = Field(..., description="The type of tool that was executed")
    raw_results: List[Dict[str, Any]] = Field(
        ..., description="The raw results from the tool"
    )
    processed_results: str = Field(
        ..., description="The processed results in a format suitable for the LLM"
    )
    error: Optional[str] = Field(
        None, description="Any error that occurred during tool execution"
    )


class AgentResponse(BaseModel):
    """Schema for the final agent response"""

    answer: str = Field(..., description="The answer to the user's query")
    sources: List[Dict[str, str]] = Field(
        ..., description="The sources used to generate the answer"
    )
    confidence: float = Field(..., description="The confidence in the answer (0-1)")


class AgentState(BaseModel):
    """Schema for the agent state"""

    query: str = Field(..., description="The original query from the user")
    query_understanding: Optional[QueryUnderstanding] = Field(
        None, description="The output of the query understanding node"
    )
    tool_selection: Optional[ToolSelection] = Field(
        None, description="The output of the tool selection node"
    )
    tool_execution_result: Optional[ToolExecutionResult] = Field(
        None, description="The output of the tool execution node"
    )
    response: Optional[AgentResponse] = Field(
        None, description="The final response from the agent"
    )
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list, description="The conversation history"
    )
