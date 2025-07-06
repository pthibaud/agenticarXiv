import sys
import traceback
import asyncio
from agents.simple_arxiv_mcp_agent import arXivAgent

from config import OLLAMA_CONFIG

async def main():

    """Main function that starts the agent and processes a question."""
    # Load environment variables
    if not OLLAMA_CONFIG:
        print("Error: OPENAI_CONFIG is not set. Please check your configuration.")
        sys.exit(1)
    # Get the OpenAI API key from the configuration
    openai_api_key = OLLAMA_CONFIG.get("api_key")

    if not openai_api_key:
        print("Error: OPENAI_API_KEY is not set in the environment or .env file")
        sys.exit(1)

    # Start the agent
    agent = arXivAgent(openai_api_key)

    # Ask for user input or use a default question
    user_question = input(
        "Enter your scientific question (or press Enter for a default): ").strip()
    if not user_question:
        user_question = "What are the latest developments in spintronics?"

    try:
        # Perform the conversation
        response = await agent.run_conversation(
            user_question,
            OLLAMA_CONFIG.get("default_model") or "mistral"
        )
        print("\nAgent Response:")
        print(response)
    except Exception as e:
        print(f"Error running agent: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    # Start the main function
    asyncio.run(main())