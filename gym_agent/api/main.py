from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import logging

from gym_agent.agents.graph_agent import GraphAgent
from gym_agent.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(title="Gym Agent API", description="API for the Gym Agent")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create agent instance
agent = GraphAgent()


class QueryRequest(BaseModel):
    """Request model for the query endpoint"""

    query: str
    conversation_history: Optional[List[Dict[str, str]]] = None


class QueryResponse(BaseModel):
    """Response model for the query endpoint"""

    answer: str


@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the agent

    Args:
        request: The query request

    Returns:
        The agent's response
    """
    try:
        # Run the agent
        response = agent.run(
            query=request.query, conversation_history=request.conversation_history or []
        )

        # Return the response
        return QueryResponse(answer=response)
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/api/health")
async def health():
    """
    Health check endpoint

    Returns:
        Health status
    """
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("gym_agent.api.main:app", host="0.0.0.0", port=8000, reload=True)
