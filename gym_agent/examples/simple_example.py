"""
Simple example of using the Gym Agent
"""

from gym_agent.agents.graph_agent import GraphAgent


def main():
    """
    Main function
    """
    # Create agent
    agent = GraphAgent()

    # Run agent with a query
    query = "What are the key concepts in LLM inference?"
    print(f"Query: {query}")

    response = agent.run(query)
    print(f"Response: {response}")

    # Run agent with a follow-up query
    conversation_history = [
        {"role": "user", "content": query},
        {"role": "assistant", "content": response},
    ]

    follow_up_query = "How does KV-Cache optimization work?"
    print(f"\nFollow-up Query: {follow_up_query}")

    follow_up_response = agent.run(follow_up_query, conversation_history)
    print(f"Response: {follow_up_response}")


if __name__ == "__main__":
    main()
