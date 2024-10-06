from qdrant_client import QdrantClient
from typing import Optional
from meilisearch import Client as MeilisearchClient
from qdrant_client import models
from gym_reader.data_models import PayloadForIndexing
from openai import OpenAI
from gym_reader.logger import get_logger

log = get_logger(__name__)


class GymIndex:
    def __init__(
        self,
        qdrant_client: QdrantClient,
        meilisearch_client: MeilisearchClient,
        openai_client: OpenAI,
    ):
        self.qdrant_client = qdrant_client
        self.meilisearch_client = meilisearch_client
        self.openai_client = openai_client
        self.default_embedding_dimension_for_summary = 1536
        self.default_embedding_provider_for_summary = "openai"
        self.default_embedding_dimension_for_content = 1536
        self.default_embedding_provider_for_content = "openai"

    def get_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small",
        dimension: Optional[int] = 1536,
        provider: str = "openai",
    ):
        try:
            # assume 1 word = 3 tokens (for simplicity)
            # TODO: use tiktoken
            MAX_TOKENS = 7000
            MAX_WORDS = MAX_TOKENS // 3
            TEXT_WORDS = len(text.split())
            if TEXT_WORDS > MAX_WORDS:
                words = text.split()
                text = " ".join(words[:MAX_WORDS])
                log.info(f"Text trimmed to {MAX_WORDS} words for embedding.")
            response = self.openai_client.embeddings.create(
                model=model,
                input=text,
                encoding_format="float",
                dimensions=dimension,
            )
            return response.data[0].embedding
        except Exception as e:
            log.error(f"Error getting embedding: {e}", exc_info=True)
            raise e

    def search_from_collection(self, query: str, collection_name: str, limit: int = 10):
        # Search the summary Index
        summary_embedding = self.get_embedding(
            query,
            dimension=self.default_embedding_dimension_for_summary,
            provider=self.default_embedding_provider_for_summary,
        )
        # Search the content Index
        content_embedding = self.get_embedding(
            query,
            dimension=self.default_embedding_dimension_for_content,
            provider=self.default_embedding_provider_for_content,
        )
        # Combine the results
        results = self.qdrant_client.query_points(
            collection_name,
            prefetch=[
                models.Prefetch(
                    query=list(summary_embedding.flatten()),
                    using="summary",
                    limit=limit,
                ),
                models.Prefetch(
                    query=list(content_embedding.flatten()),
                    using="content",
                    limit=limit,
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
        )
        return results

    def add_to_qdrant_collection(self, data: PayloadForIndexing, collection_name: str):
        existing_collections = [
            collection.name
            for collection in self.qdrant_client.get_collections().collections
        ]
        if collection_name not in existing_collections:
            # create collection with default params
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "summary": models.VectorParams(
                        size=self.default_embedding_dimension_for_summary,
                        distance=models.Distance.COSINE,
                    ),
                    "content": models.VectorParams(
                        size=self.default_embedding_dimension_for_content,
                        distance=models.Distance.COSINE,
                    ),
                },
            )
            try:
                # we will create a payload index for "parent_link" so that we can easily delete by this field
                self.qdrant_client.create_payload_index(
                    collection_name=collection_name,
                    field_name="parent_link",
                    field_schema="keyword",  # Create a keyword based schem on the parent_link field
                )
            except Exception as e:
                log.error(f"Error creating payload index: {e}", exc_info=True)
                raise e
        points = [
            # we will assign a random id to the point
            models.PointStruct(
                id=data.uuid,
                vector={
                    # we have two vectors for each point one for summary and one for content
                    "summary": self.get_embedding(data.parent_summary),
                    "content": self.get_embedding(data.parent_content),
                },
                payload=data.model_dump(),
            )
        ]
        try:
            self.qdrant_client.upsert(collection_name=collection_name, points=points)
            return True
        except Exception as e:
            log.error(f"Error adding to qdrant collection: {e}", exc_info=True)
            raise e

    def delete_from_qdrant_collection(self, point_ids: list[str], collection_name: str):
        try:
            self.qdrant_client.delete(collection_name=collection_name, points=point_ids)
        except Exception as e:
            log.error(f"Error deleting from qdrant collection: {e}", exc_info=True)
            raise e

    def add_to_meilisearch_collection(self, data, collection_name: str):
        # let us check if the collection exists
        indexes = self.meilisearch_client.get_indexes()
        existing_collection_names = [index.uid for index in indexes["results"]]
        if collection_name not in existing_collection_names:
            # create collection with default params
            self.meilisearch_client.create_index(
                collection_name, {"primaryKey": "uuid"}
            )
            # TODO: move the settings to a config file
            self.meilisearch_client.index(collection_name).update_settings(
                {
                    "rankingRules": [
                        "words",
                        "typo",
                        "proximity",
                        "attribute",
                        "sort",
                        "exactness",
                    ],
                    "distinctAttribute": "parent_link",
                    "searchableAttributes": [
                        "parent_link",
                        "parent_summary",
                        "parent_keywords",
                        "parent_title",
                    ],
                    "displayedAttributes": [
                        "parent_link",
                        "parent_title",
                        "parent_keywords",
                        "parent_content",
                    ],
                    "sortableAttributes": ["parent_link", "parent_title"],
                    "typoTolerance": {
                        "minWordSizeForTypos": {"oneTypo": 8, "twoTypos": 10},
                        "disableOnAttributes": ["title"],
                    },
                    "pagination": {"maxTotalHits": 5000},
                    "faceting": {"maxValuesPerFacet": 200},
                    "searchCutoffMs": 150,
                }
            )
        try:
            # add the data to the collection
            self.meilisearch_client.index(collection_name).add_documents(
                data.model_dump()
            )
            return True
        except Exception as e:
            log.error(f"Error adding to meilisearch collection: {e}", exc_info=True)
            raise e

    def delete_from_meilisearch_collection(self, data, collection_name: str):
        pass
