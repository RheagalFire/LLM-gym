from gym_reader.semantic_search.preprocessor import (
    Preprocessor,
)  # Import the Preprocessor class
from qdrant_client import QdrantClient, models  # Imported models
from meilisearch import Client as MeilisearchClient
from gym_reader.data_models import SearchResult
from openai import OpenAI


class HybridSearch(Preprocessor):  # Inherit from Preprocessor
    def __init__(
        self,
        qdrant_client: QdrantClient,
        meilisearch_client: MeilisearchClient,
        openai_client: OpenAI,
    ):
        super().__init__(qdrant_client, meilisearch_client, openai_client)

    def search(self, query: str, collection_name: str, limit: int = 3) -> SearchResult:
        results = self.search_from_collection(query, collection_name, limit)
        self.logger.debug(results)
        # parent link content
        return SearchResult(
            summary=[
                {result.payload["parent_link"]: result.payload["parent_summary"]}
                for result in results.points
            ],
            content_score=[result.score for result in results.points],
            summary_score=[result.score for result in results.points],
            relevant_content=[
                result.payload["parent_content"] for result in results.points
            ],
        )

    def search_from_collection(self, query: str, collection_name: str, limit: int = 10):
        summary_embedding = self.get_embedding(
            query,
            dimension=self.default_embedding_dimension_for_summary,
            provider=self.default_embedding_provider_for_summary,
        )
        content_embedding = self.get_embedding(
            query,
            dimension=self.default_embedding_dimension_for_content,
            provider=self.default_embedding_provider_for_content,
        )
        results = self.qdrant_client.query_points(
            collection_name,
            prefetch=[
                models.Prefetch(
                    query=summary_embedding,
                    using="summary",
                    limit=limit,
                ),
                models.Prefetch(
                    query=content_embedding,
                    using="content",
                    limit=limit,
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
        )
        return results
