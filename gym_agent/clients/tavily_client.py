from tavily import TavilyClient as BaseTavilyClient
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from typing import Dict, Any
from gym_agent.settings import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()


class TavilyClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.client = BaseTavilyClient(api_key=settings.TAVILY_API_KEY)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def _search_with_retry(
        self, query: str, search_depth: str = "basic"
    ) -> Dict[str, Any]:
        """
        Perform a search using Tavily
        """
        return self.client.search(query=query, search_depth=search_depth)

    def search(self, query: str, search_depth: str = "basic") -> Dict[str, Any]:
        """
        Perform a search using Tavily API with exponential retry.

        Args:
            query: The search query
            search_depth: The search depth (basic or comprehensive)

        Returns:
            The search results
        """
        try:
            return self._search_with_retry(query, search_depth)
        except RetryError as e:
            logger.error(f"All retry attempts failed for Tavily search: {e}")
            return {"results": []}
        except Exception as e:
            logger.error(f"Unexpected error in Tavily search: {e}")
            return {"results": []}


# Create a single instance of TavilyClient
tavily_client = TavilyClient()
