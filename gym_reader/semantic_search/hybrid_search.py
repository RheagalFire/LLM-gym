from qdrant_client import QdrantClient
from meilisearch import Client as MeilisearchClient
from gym_reader.data_models import SearchResult
from openai import OpenAI
from gym_reader.logger import get_logger
from gym_reader.semantic_search.index import GymIndex
from typing import List

log = get_logger(__name__)


class HybridSearch(GymIndex):
    def __init__(
        self,
        qdrant_client: QdrantClient,
        meilisearch_client: MeilisearchClient,
        openai_client: OpenAI,
    ):
        super().__init__(qdrant_client, meilisearch_client, openai_client)

    def search(
        self, query: str, collection_name: str, limit: int = 2
    ) -> List[SearchResult]:
        # Search the summary Index
        results = self.search_from_collection(query, collection_name, limit)
        log.debug(results)
        return [
            SearchResult(
                summary=[
                    {result.payload["parent_link"]: result.payload["parent_summary"]}
                ],
                content_score=[result.score],
                summary_score=[result.score],
                entire_content_of_the_link=[result.payload["parent_content"]],
            )
            for result in results.points
        ]
