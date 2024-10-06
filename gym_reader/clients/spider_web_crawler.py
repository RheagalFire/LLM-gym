from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from typing import Dict, Any
import requests
from gym_reader.settings import get_settings
from gym_reader.logger import get_logger

log = get_logger(__name__)
settings = get_settings()


class SpiderClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.api_key = settings.SPIDER_API_KEY
        self.base_url = "https://api.spider.cloud/crawl"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def _search_with_retry(self, url: str) -> Dict[str, Any]:
        """
        Perform a search using Spider API
        """
        json_data = {"url": url, "limit": 2, "return_format": "markdown"}
        response = requests.post(self.base_url, headers=self.headers, json=json_data)
        response.raise_for_status()
        return response.json()

    def search(self, url: str) -> str:
        """
        Perform a search using Spider API with exponential retry.
        """
        try:
            return self._search_with_retry(url)
        except RetryError as e:
            log.error(f"All retry attempts failed for Spider search: {e}")
            return {}
        except Exception as e:
            log.error(f"Unexpected error in Spider search: {e}")
            raise


# Create a single instance of SpiderClient
spider_client = SpiderClient()

if __name__ == "__main__":
    result = spider_client.search("https://github.com/orgs/openai/repositories")
    log.debug("Spider search result:", result)
