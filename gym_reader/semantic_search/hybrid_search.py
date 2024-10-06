from qdrant_client import QdrantClient
from gym_reader.data_models import SearchResult


class HybridSearch:
    def __init__(self, qdrant_client: QdrantClient):
        self.qdrant_client = qdrant_client

    def search(self, query: str, collection_name: str) -> SearchResult:
        pass
