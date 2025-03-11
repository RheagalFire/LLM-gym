from qdrant_client import QdrantClient
from gym_agent.settings import get_settings

settings = get_settings()


class GymAgentQdrantClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            port=settings.QDRANT_PORT,
        )

    def get_client(self):
        return self.client

    def search(self, collection_name, query_vector, limit=5):
        """
        Search for similar vectors in the collection.

        Args:
            collection_name: The name of the collection to search in
            query_vector: The query vector
            limit: The maximum number of results to return

        Returns:
            The search results
        """
        return self.client.search(
            collection_name=collection_name, query_vector=query_vector, limit=limit
        )


qdrant_client = GymAgentQdrantClient().get_client()
