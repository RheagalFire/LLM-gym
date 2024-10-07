from qdrant_client import QdrantClient
from typing import Optional
from meilisearch import Client as MeilisearchClient
from qdrant_client import models
from gym_reader.data_models import PayloadForIndexing
from openai import OpenAI
from gym_reader.logger import get_logger
from fastembed import TextEmbedding
import tiktoken

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
        self.text_embedding_model = TextEmbedding("BAAI/bge-base-en")
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # Initialize tokenizer

    def get_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small",
        dimension: Optional[int] = 1536,
        provider: str = "openai",
    ):
        if provider == "openai":
            try:
                # assume 1 word = 4 tokens (for simplicity)
                # TODO: use tiktoken
                MAX_TOKENS = 7000
                tokens = self.tokenizer.encode(text)
                # TODO: 1. Use Averaging of the embedding for the truncated text
                # TODO: 2. Chunk Different parts of the text and embed them separately
                if len(tokens) > MAX_TOKENS:
                    tokens = tokens[:MAX_TOKENS]
                    text = self.tokenizer.decode(tokens)
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
        else:
            # it will only process 512 sequence at length
            return list(self.text_embedding_model.embed(text))

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

    def check_if_link_exists(self, link: str, collection_name: str):
        # First check if the collection exists or not
        existing_collections = [
            collection.name
            for collection in self.qdrant_client.get_collections().collections
        ]
        if collection_name not in existing_collections:
            return False
        # let's check if the link exists in the qdrant collection
        results = self.qdrant_client.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                should=[
                    models.FieldCondition(
                        key="parent_link", match=models.MatchValue(value=link)
                    )
                ]
            ),
            limit=1,
        )
        if results:
            return True
        return False

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
