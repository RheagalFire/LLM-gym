import argparse
import logging
from typing import List, Dict, Any
import json

from gym_agent.agents.graph_agent import GraphAgent
from gym_agent.settings import get_settings

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
        "--history", "-H", type=str, help="Path to a JSON file containing conversation history"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument(
        "--debug", "-d", action="store_true", help="Enable debug mode"
    )
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Create agent
    logger.info("Creating Graph Agent")
    agent = GraphAgent()
    
    # Load conversation history if provided
    conversation_history = []
    if args.history:
        try:
            logger.info(f"Loading conversation history from {args.history}")
            with open(args.history, "r") as f:
                conversation_history = json.load(f)
            logger.info(f"Loaded {len(conversation_history)} messages from history")
        except Exception as e:
            logger.error(f"Error loading conversation history: {str(e)}")
            conversation_history = []
    
    # Run in interactive mode
    if args.interactive:
        logger.info("Starting interactive mode")
        print("Gym Agent CLI (Interactive Mode)")
        print("Type 'exit' or 'quit' to exit")
        print("Type 'history' to view conversation history")
        print("Type 'save <filename>' to save conversation history")
        print("Type 'debug on/off' to toggle debug mode")
        print()
        
        debug_mode = args.debug
        
        while True:
            # Get query
            query = input("You: ")
            
            # Check for commands
            if query.lower() in ["exit", "quit"]:
                logger.info("Exiting interactive mode")
                break
            elif query.lower() == "history":
                logger.debug("Displaying conversation history")
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
                    logger.info(f"Saving conversation history to {filename}")
                    with open(filename, "w") as f:
                        json.dump(conversation_history, f, indent=2)
                    print(f"Conversation history saved to {filename}")
                except Exception as e:
                    logger.error(f"Error saving conversation history: {str(e)}")
                    print(f"Error saving conversation history: {str(e)}")
                continue
            elif query.lower() == "debug on":
                debug_mode = True
                logging.getLogger('gym_agent').setLevel(logging.DEBUG)
                logger.debug("Debug mode enabled")
                print("Debug mode enabled")
                continue
            elif query.lower() == "debug off":
                debug_mode = False
                logging.getLogger('gym_agent').setLevel(logging.INFO)
                logger.info("Debug mode disabled")
                print("Debug mode disabled")
                continue
            
            # Run agent
            try:
                logger.info(f"Processing query: '{query}'")
                response = agent.run(query=query, conversation_history=conversation_history, debug=debug_mode)
                print(f"Agent: {response}")
                
                # Update conversation history
                conversation_history.append({"role": "user", "content": query})
                conversation_history.append({"role": "assistant", "content": response})
                logger.debug(f"Conversation history updated, now has {len(conversation_history)} messages")
            except Exception as e:
                logger.error(f"Error running agent: {str(e)}")
                logger.exception("Detailed traceback:")
                print(f"Error: {str(e)}")
    
    # Run with single query
    elif args.query:
        try:
            logger.info(f"Processing single query: '{args.query}'")
            response = agent.run(query=args.query, conversation_history=conversation_history, debug=args.debug)
            print(response)
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}")
            logger.exception("Detailed traceback:")
            print(f"Error: {str(e)}")
    
    # No query provided
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
