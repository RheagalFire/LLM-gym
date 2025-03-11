from gym_reader.agents.base_agent import Agent
from gym_reader.clients.postgres_mcp_client import PostgresMCPClient, get_client
import asyncio
import traceback
from typing import List, Dict, Any, Optional


class PostgresChatbotAgent(Agent):
    """
    Chatbot agent that interacts with the Postgres MCP server
    """

    def __init__(self, programme=None):
        """
        Initialize the Postgres chatbot agent

        Args:
            programme: Optional programme to use for the agent
        """
        super().__init__(programme)
        self.postgres_client = None
        self.conversation_history = []

    async def initialize(self, server_url: str = "http://localhost:8000"):
        """
        Initialize the Postgres client

        Args:
            server_url: URL of the Postgres MCP server
        """
        try:
            self.postgres_client = await get_client(server_url)
            # Ensure the client is connected
            await self.postgres_client.connect()
            return True
        except Exception as e:
            print(f"Error initializing client: {str(e)}")
            traceback.print_exc()
            return False

    async def get_unindexed_files(self) -> List[Dict[str, Any]]:
        """
        Get unindexed files from the Postgres server

        Returns:
            List of unindexed files
        """
        try:
            if not self.postgres_client:
                success = await self.initialize()
                if not success:
                    return []

            files = await self.postgres_client.get_unindexed_files()

            # Ensure we return a list
            if not isinstance(files, list):
                if isinstance(files, dict):
                    return [files]
                return []

            return files
        except Exception as e:
            print(f"Error getting unindexed files: {str(e)}")
            traceback.print_exc()
            return []

    async def get_indexed_files(self) -> List[Dict[str, Any]]:
        """
        Get indexed files from the Postgres server
        """
        try:
            if not self.postgres_client:
                success = await self.initialize()
                if not success:
                    return []

            files = await self.postgres_client.get_indexed_files()
            return files
        except Exception as e:
            print(f"Error getting indexed files: {str(e)}")
            traceback.print_exc()

    async def process_message(self, message: str) -> str:
        """
        Process a user message and generate a response

        Args:
            message: User message

        Returns:
            Agent response
        """
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})

        # Process the message based on content
        response = ""

        if "unindexed files" in message.lower() or "get files" in message.lower():
            try:
                files = await self.get_unindexed_files()
                if files and len(files) > 0:
                    response = f"I found {len(files)} unindexed files. Here are the first few:\n"
                    for i, file in enumerate(files[:5]):
                        file_id = file.get("id", "unknown")
                        file_name = file.get("name", "unnamed")
                        response += f"{i+1}. ID: {file_id}, Name: {file_name}\n"

                    if len(files) > 5:
                        response += f"...and {len(files) - 5} more files."
                else:
                    response = "I didn't find any unindexed files."
            except Exception as e:
                response = f"Sorry, I encountered an error while fetching unindexed files: {str(e)}"
                traceback.print_exc()
        elif (
            "indexed files" in message.lower() or "get indexed files" in message.lower()
        ):
            try:
                files = await self.get_indexed_files()
                if files and len(files) > 0:
                    response = f"I found {len(files)} indexed files. Here are the first few:\n{files}"
                    # for i, file in enumerate(files[:5]):
                    #     file_id = file.get("id", "unknown")
                    #     file_name = file.get("name", "unnamed")
                    #     response += f"{i+1}. ID: {file_id}, Name: {file_name}\n"

                    # if len(files) > 5:
                    #     response += f"...and {len(files) - 5} more files."
                else:
                    response = "I didn't find any indexed files."
            except Exception as e:
                response = f"Sorry, I encountered an error while fetching indexed files: {str(e)}"
                traceback.print_exc()
        else:
            # Default response for other queries
            response = "I'm a Postgres chatbot. You can ask me about unindexed files in the database."

        # Add agent response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})

        return response

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history

        Returns:
            List of conversation messages
        """
        return self.conversation_history

    async def close(self):
        """
        Close the client connection
        """
        if self.postgres_client:
            try:
                await self.postgres_client.close()
            except Exception as e:
                print(f"Error closing client: {str(e)}")
                traceback.print_exc()


# Example usage
async def main():
    # Create an agent instance
    agent = PostgresChatbotAgent()

    try:
        # Initialize the agent
        success = await agent.initialize()
        if not success:
            print("Failed to initialize agent")
            return None

        # Example interaction
        response = await agent.process_message("Can you show me the unindexed files?")
        print(response)
    except Exception as e:
        print(f"Error in main: {str(e)}")
        traceback.print_exc()
    finally:
        # Close the connection
        await agent.close()

    return agent


if __name__ == "__main__":
    agent = asyncio.run(main())
