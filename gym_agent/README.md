# Gym Agent

A Graph Agent implementation using LangGraph with access to Qdrant and MeiliSearch via MCP.

## Features

- Graph-based agent architecture using LangGraph
- Direct OpenAI integration (without LangChain)
- Vector search capabilities using Qdrant
- Keyword search capabilities using MeiliSearch
- Web search capabilities
- Modular Capability Provider (MCP) integration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure environment variables are set in `.env` file:
```
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
MEILISEARCH_URL=your_meilisearch_url
MEILISEARCH_MASTER_KEY=your_meilisearch_master_key
TAVILY_API_KEY=your_tavily_api_key
```

## Usage

### Running the Agent

```python
from gym_agent.agents.graph_agent import GraphAgent

agent = GraphAgent()
response = agent.run("Your query here")
print(response)
```

### Running the API Server

```bash
python -m gym_agent.api.main
```

## Architecture

The agent uses a graph-based architecture with the following components:

1. **Nodes**:
   - Query Understanding
   - Tool Selection
   - Tool Execution
   - Response Generation

2. **Tools**:
   - Qdrant Vector Search
   - MeiliSearch Keyword Search
   - Web Search

3. **Clients**:
   - OpenAI Client
   - Qdrant Client
   - MeiliSearch Client
   - Tavily Client (for web search)

## License

This project is licensed under the same license as the parent project. 