import argparse
import logging
from typing import List, Dict, Any
import json

from gym_agent.agents.graph_agent import GraphAgent
from gym_agent.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


def main():
    """
    Main CLI function
    """
    # Parse arguments
    parser = argparse.ArgumentParser(description="Gym Agent CLI")
    parser.add_argument("--query", "-q", type=str, help="The query to run the agent on")
    parser.add_argument(
        "--history",
        "-H",
        type=str,
        help="Path to a JSON file containing conversation history",
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )
    args = parser.parse_args()

    # Create agent
    agent = GraphAgent()

    # Load conversation history if provided
    conversation_history = []
    if args.history:
        try:
            with open(args.history, "r") as f:
                conversation_history = json.load(f)
        except Exception as e:
            logger.error(f"Error loading conversation history: {str(e)}")
            conversation_history = []

    # Run in interactive mode
    if args.interactive:
        print("Gym Agent CLI (Interactive Mode)")
        print("Type 'exit' or 'quit' to exit")
        print("Type 'history' to view conversation history")
        print("Type 'save <filename>' to save conversation history")
        print()

        while True:
            # Get query
            query = input("You: ")

            # Check for commands
            if query.lower() in ["exit", "quit"]:
                break
            elif query.lower() == "history":
                print("\nConversation History:")
                for i, message in enumerate(conversation_history):
                    role = message["role"]
                    content = message["content"]
                    print(f"{i+1}. {role.capitalize()}: {content}")
                print()
                continue
            elif query.lower().startswith("save "):
                filename = query[5:].strip()
                try:
                    with open(filename, "w") as f:
                        json.dump(conversation_history, f, indent=2)
                    print(f"Conversation history saved to {filename}")
                except Exception as e:
                    print(f"Error saving conversation history: {str(e)}")
                continue

            # Run agent
            try:
                response = agent.run(
                    query=query, conversation_history=conversation_history
                )
                print(f"Agent: {response}")

                # Update conversation history
                conversation_history.append({"role": "user", "content": query})
                conversation_history.append({"role": "assistant", "content": response})
            except Exception as e:
                logger.error(f"Error running agent: {str(e)}")
                print(f"Error: {str(e)}")

    # Run with single query
    elif args.query:
        try:
            response = agent.run(
                query=args.query, conversation_history=conversation_history
            )
            print(response)
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}")
            print(f"Error: {str(e)}")

    # No query provided
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
