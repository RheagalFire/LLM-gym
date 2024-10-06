from tavily import TavilyClient as BaseTavilyClient
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from typing import Dict, Any
from gym_reader.settings import get_settings
from gym_reader.logger import get_logger

log = get_logger(__name__)
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
    def _search_with_retry(self, query: str) -> Dict[str, Any]:
        """
        Perform a search using Tavily
        """
        return self.client.search(query)

    def search(self, query: str) -> Dict[str, Any]:
        """
        Perform a search using Tavily API with exponential retry.
        """
        try:
            return self._search_with_retry(query)
        except RetryError as e:
            log.error(f"All retry attempts failed for Tavily search: {e}")
            return {}
        except Exception as e:
            log.error(f"Unexpected error in Tavily search: {e}")
            raise


# Create a single instance of TavilyClient
tavily_client = TavilyClient()

if __name__ == "__main__":
    result = tavily_client.search(
        "microsoft community: microsoft teams screen share goes blank"
    )
    log.debug("Tavily search result:", result)
