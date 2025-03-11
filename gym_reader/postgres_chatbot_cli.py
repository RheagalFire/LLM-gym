#!/usr/bin/env python3
import asyncio
import argparse
import traceback
from gym_reader.agents.postgres_chatbot_agent import PostgresChatbotAgent


async def chat_loop(agent, server_url=None):
    """
    Run an interactive chat loop with the Postgres chatbot agent

    Args:
        agent: PostgresChatbotAgent instance
        server_url: Optional server URL to connect to
    """
    try:
        # Initialize the agent
        if server_url:
            success = await agent.initialize(server_url)
        else:
            success = await agent.initialize()

        if not success:
            print(
                "Failed to initialize the chatbot. Please check if the server is running."
            )
            return

        print(
            "Postgres Chatbot initialized. Type 'exit' or 'quit' to end the conversation."
        )
        print(
            "You can ask about unindexed files by typing 'show unindexed files' or similar queries."
        )
        print(
            "You can also ask about indexed files by typing 'show indexed files' or similar queries."
        )
        print("-" * 50)

        while True:
            # Get user input
            user_input = input("You: ")

            # Check if user wants to exit
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Chatbot: Goodbye!")
                break

            try:
                # Process the message and get a response
                response = await agent.process_message(user_input)

                # Display the response
                print(f"Chatbot: {response}")
                print("-" * 50)
            except Exception as e:
                print(f"Error processing message: {str(e)}")
                traceback.print_exc()
                print("-" * 50)
    except Exception as e:
        print(f"Error in chat loop: {str(e)}")
        traceback.print_exc()
    finally:
        # Ensure we close the connection
        try:
            await agent.close()
        except Exception as e:
            print(f"Error closing agent: {str(e)}")
            traceback.print_exc()


def main():
    """
    Main entry point for the Postgres chatbot CLI
    """
    parser = argparse.ArgumentParser(description="Postgres Chatbot CLI")
    parser.add_argument(
        "--server-url",
        type=str,
        default="http://localhost:8000",
        help="URL of the Postgres MCP server (default: http://localhost:8000)",
    )

    args = parser.parse_args()

    # Create the agent
    agent = PostgresChatbotAgent()

    try:
        # Run the chat loop
        asyncio.run(chat_loop(agent, args.server_url))
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
