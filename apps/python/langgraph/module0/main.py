"""
Module for interacting with LLM models and search functionality.
Provides a clean interface for chat completions and search operations.
"""
import pathlib
from typing import List, Dict, Any
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from mylibrary import initialize_environment

@dataclass
class Config:
    """Configuration for LLM models and search tools."""
    gpt4_model: str = "gpt-4o"
    gpt35_model: str = "gpt-3.5-turbo-0125"
    temperature: float = 0
    max_search_results: int = 3

class LLMService:
    """Service for handling LLM interactions."""

    def __init__(self, config: Config):
        """Initialize LLM models."""
        self.config = config
        self.gpt4_chat = ChatOpenAI(
            model=config.gpt4_model,
            temperature=config.temperature
        )
        self.gpt35_chat = ChatOpenAI(
            model=config.gpt35_model,
            temperature=config.temperature
        )
        self.search_tool = TavilySearchResults(
            max_results=config.max_search_results
        )

    def chat_with_gpt4(self, message: str | List[HumanMessage]) -> str:
        """Send a message to GPT-4 model."""
        return self.gpt4_chat.invoke(message)

    def chat_with_gpt35(self, message: str | List[HumanMessage]) -> str:
        """Send a message to GPT-3.5 model."""
        return self.gpt35_chat.invoke(message)

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Perform a search using Tavily."""
        return self.search_tool.invoke(query)

def main() -> None:
    """Main execution function."""
    # Initialize environment
    current_dir = pathlib.Path(__file__).parent
    dotenv_path = current_dir / ".env"
    initialize_environment(str(dotenv_path))

    # Create service with default config
    llm_service = LLMService(Config())

    # Example usage
    print("Testing LLM Service:")

    # Test chat
    message = HumanMessage(content="Hello world", name="Lance")
    # print("\nGPT-4 Response:")
    print(llm_service.chat_with_gpt4([message]))

    print("\nGPT-3.5 Response:")
    print(llm_service.chat_with_gpt35("hello world"))

    # Test search
    print("\nSearch Results for 'What is LangGraph?':")
    search_results = llm_service.search("What is LangGraph?")
    print(search_results)


if __name__ == "__main__":
    main()
