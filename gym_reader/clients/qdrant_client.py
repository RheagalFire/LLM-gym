from qdrant_client import QdrantClient
from gym_reader.settings import get_settings

settings = get_settings()


class GymReaderQdrantClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)  # Use super() without arguments
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY
        )

    def get_client(self):
        return self.client


qdrant_client = GymReaderQdrantClient().get_client()
