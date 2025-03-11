from meilisearch import Client as MeiliClient
from gym_agent.settings import get_settings

settings = get_settings()


class GymAgentMeiliSearchClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        self.client = MeiliClient(
            settings.MEILISEARCH_URL, settings.MEILISEARCH_MASTER_KEY
        )

    def get_client(self):
        return self.client

    def search(self, index_name, query, limit=5, search_settings=None):
        """
        Search for documents in the index.

        Args:
            index_name: The name of the index to search in
            query: The search query
            limit: The maximum number of results to return
            search_settings: Additional search settings

        Returns:
            The search results
        """
        if search_settings is None:
            search_settings = {
                "limit": limit,
                "attributesToHighlight": ["*"],
                "highlightPreTag": "<em>",
                "highlightPostTag": "</em>",
            }

        return self.client.index(index_name).search(query, search_settings)


meilisearch_client = GymAgentMeiliSearchClient().get_client()
