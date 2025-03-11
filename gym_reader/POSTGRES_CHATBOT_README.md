# Postgres Chatbot

This is a chatbot that interacts with the Postgres MCP server to retrieve and display unindexed files from the database.

## Components

1. **Postgres MCP Client** (`gym_reader/clients/postgres_mcp_client.py`): A client for interacting with the Postgres MCP server.
2. **Postgres Chatbot Agent** (`gym_reader/agents/postgres_chatbot_agent.py`): An agent that uses the Postgres MCP client to process user messages and generate responses.
3. **Postgres Chatbot CLI** (`gym_reader/postgres_chatbot_cli.py`): A command-line interface for interacting with the chatbot.

## Prerequisites

- Python 3.7 or higher
- Access to the Postgres MCP server (running on `http://localhost:8000` by default)
- Required Python packages:
  - `modelcontextprotocol` (MCP SDK)
  - `asyncio` (for asynchronous programming)

## Setup Instructions

1. **Install the required packages**

   Install the Model Context Protocol SDK:

   ```bash
   pip install modelcontextprotocol
   ```

   Note: `asyncio` and `contextlib` are part of the Python standard library, so you don't need to install them separately.

2. **Ensure the Postgres MCP server is running**

   The server should be running at `http://localhost:8000` (or your specified URL). You can start the server with:

   ```bash
   python -m gym_reader.fastmcp_servers.postgres_server
   ```

3. **Run the chatbot**

   You can run the chatbot with:

   ```bash
   python -m gym_reader.postgres_chatbot_cli
   ```

## Usage

Once the chatbot is running, you can interact with it through the command line:

1. **Ask about unindexed files**:
   - "Show me unindexed files"
   - "Get files"
   - "What files need indexing?"

2. **Exit the chatbot**:
   - Type "exit", "quit", or "bye" to end the conversation

## Example Conversation

```
Postgres Chatbot initialized. Type 'exit' or 'quit' to end the conversation.
You can ask about unindexed files by typing 'show unindexed files' or similar queries.
--------------------------------------------------
You: Show me unindexed files
Chatbot: I found 3 unindexed files. Here are the first few:
1. ID: 123, Name: document1.pdf
2. ID: 124, Name: document2.pdf
3. ID: 125, Name: document3.pdf
--------------------------------------------------
You: exit
Chatbot: Goodbye!
```

## Technical Details

The chatbot uses the Model Context Protocol (MCP) to communicate with the Postgres server. The implementation:

1. Uses the official MCP SDK for communication
2. Connects to the server using stdio transport
3. Calls tools directly using the `call_tool` method
4. Ensures proper cleanup of resources when the chatbot exits

## Troubleshooting

1. **Connection Error**:
   - Ensure the Postgres MCP server is running
   - Check that the server URL is correct
   - Verify network connectivity

2. **Import Error**:
   - Ensure all required packages are installed: `pip install modelcontextprotocol`
   - Check that the project structure is correct

3. **Runtime Error**:
   - Check the error message for details
   - Ensure the database is properly configured and accessible

## Extending the Chatbot

You can extend the chatbot by:

1. Adding more endpoints to the Postgres MCP server
2. Implementing additional methods in the PostgresMCPClient class
3. Enhancing the message processing logic in the PostgresChatbotAgent class

## License

This project is licensed under the terms of your project's license. 