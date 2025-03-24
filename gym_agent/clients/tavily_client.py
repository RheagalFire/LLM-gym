from tavily import TavilyClient as BaseTavilyClient
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from typing import Dict, Any
from gym_agent.settings import get_settings
import logging
import requests
import json

# Configure more detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
        api_key = settings.TAVILY_API_KEY
        logger.debug(f"Initializing Tavily client with API key: {'[SET]' if api_key else '[NOT SET]'}")
        
        if not api_key:
            logger.warning("Tavily API key is not set. Web search will not work.")
            self.client = None
        else:
            try:
                self.client = BaseTavilyClient(api_key=api_key)
                logger.debug("Tavily client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Tavily client: {str(e)}")
                self.client = None

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
        if not self.client:
            logger.warning("Tavily client is not initialized. Cannot perform search.")
            return {"results": []}
        
        logger.debug(f"Performing Tavily search with query: '{query}', depth: {search_depth}")
        try:
            result = self.client.search(query=query, search_depth=search_depth)
            logger.debug(f"Tavily search successful, got {len(result.get('results', []))} results")
            return result
        except Exception as e:
            logger.error(f"Error in _search_with_retry: {str(e)}")
            raise

    def search(self, query: str, search_depth: str = "basic") -> Dict[str, Any]:
        """
        Perform a search using Tavily API with exponential retry.

        Args:
            query: The search query
            search_depth: The search depth (basic or comprehensive)

        Returns:
            The search results
        """
        logger.info(f"Starting Tavily search for query: '{query}' with api key: {settings.TAVILY_API_KEY}")
        try:
            results = self._search_with_retry(query, search_depth)
            logger.info(f"Tavily search completed successfully with {len(results.get('results', []))} results")
            return results
        except RetryError as e:
            logger.error(f"All retry attempts failed for Tavily search: {e}")
            return {"results": []}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error in Tavily search: {e}")
            # Log response details if available
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response headers: {e.response.headers}")
                try:
                    logger.error(f"Response body: {e.response.text}")
                except:
                    logger.error("Could not extract response body")
            return {"results": []}
        except Exception as e:
            logger.error(f"Unexpected error in Tavily search: {e}")
            return {"results": []}


# Create a single instance of TavilyClient
tavily_client = TavilyClient()


if __name__ == "__main__":
    logger.info("Testing Tavily client directly")
    results = tavily_client.search("KV Cache")
    logger.info(f"Got {len(results.get('results', []))} results")
    logger.debug(f"Results: {json.dumps(results, indent=2)}")
