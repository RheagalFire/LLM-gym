from meilisearch import Client as MeiliClient
from gym_reader.settings import get_settings

settings = get_settings()


class GymReaderMeiliSearchClient:
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


meilisearch_client = GymReaderMeiliSearchClient().get_client()
