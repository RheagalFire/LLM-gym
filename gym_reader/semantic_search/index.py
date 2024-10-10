from qdrant_client import QdrantClient
from meilisearch import Client as MeilisearchClient
from qdrant_client import models
from gym_reader.data_models import PayloadForIndexing
from openai import OpenAI
from gym_reader.logger import get_logger
from gym_reader.semantic_search.preprocessor import (
    Preprocessor,
)  # Import the new Preprocessor class

log = get_logger(__name__)


class GymIndex(Preprocessor):
    def __init__(
        self,
        qdrant_client: QdrantClient,
        meilisearch_client: MeilisearchClient,
        openai_client: OpenAI,
    ):
        super().__init__(
            qdrant_client, meilisearch_client, openai_client
        )  # Initialize Preprocessor

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

    def delete_from_qdrant_collection(self, links: list[str], collection_name: str):
        try:
            results, offset = self.qdrant_client.scroll(
                collection_name=collection_name,
                scroll_filter=models.Filter(
                    should=[
                        models.FieldCondition(
                            key="parent_link", match=models.MatchAny(any=links)
                        )
                    ]
                ),
                limit=1000,
            )
            # get the point ids
            point_ids = [result.id for result in results]
            # delete the points
            try:
                self.qdrant_client.delete(
                    collection_name=collection_name, points_selector=point_ids
                )
            except Exception as e:
                log.error(f"Error deleting from qdrant collection: {e}", exc_info=True)
                raise e
            return True
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
                        "parent_summary",
                        "parent_title",
                        "parent_keywords",
                    ],
                    "sortableAttributes": ["parent_link", "parent_title"],
                    "typoTolerance": {
                        "minWordSizeForTypos": {"oneTypo": 8, "twoTypos": 10},
                        "disableOnAttributes": ["parent_summary"],
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

    def delete_from_meilisearch_collection(self, links, collection_name: str):
        filter = f"parent_link IN {links}"
        self.meilisearch_client.index(collection_name).delete_documents(filter=filter)
