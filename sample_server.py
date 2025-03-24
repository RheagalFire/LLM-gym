"""
Simple example of using the Gym Agent
"""

from gym_agent.agents.graph_agent import GraphAgent
import logging
import argparse


def main():
    """
    Main function
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run a simple example of the Gym Agent")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    parser.add_argument("--query", "-q", type=str, help="Custom query to run")
    parser.add_argument("--follow-up", "-f", type=str, help="Custom follow-up query")
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
    
    # Run agent with a query
    query = args.query or "What are the key concepts in LLM inference?"
    logger.info(f"Running query: {query}")
    print(f"Query: {query}")
    
    response = agent.run(query, debug=True)
    print(f"Response: {response}")
    
    # Run agent with a follow-up query
    conversation_history = [
        {"role": "user", "content": query},
        {"role": "assistant", "content": response}
    ]
    
    follow_up_query = args.follow_up or "How does KV-Cache optimization work?"
    logger.info(f"Running follow-up query: {follow_up_query}")
    print(f"\nFollow-up Query: {follow_up_query}")
    
    follow_up_response = agent.run(follow_up_query, conversation_history, debug=args.debug)
    print(f"Response: {follow_up_response}")


if __name__ == "__main__":
    main()
