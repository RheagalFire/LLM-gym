from typing import Optional
from qdrant_client import QdrantClient  # Imported models
from gym_db.db_funcs import DbOps
from gym_reader.clients.prisma_client import prisma_singleton
from meilisearch import Client as MeilisearchClient
from openai import OpenAI
from gym_reader.logger import get_logger
from fastembed import TextEmbedding
import tiktoken


class Preprocessor:
    def __init__(
        self,
        qdrant_client: QdrantClient,
        meilisearch_client: MeilisearchClient,
        openai_client: OpenAI,
    ):
        self.qdrant_client = qdrant_client
        self.meilisearch_client = meilisearch_client
        self.openai_client = openai_client
        # Embedding Model and Tokenizer
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # Initialize tokenizer
        self.text_embedding_model = TextEmbedding("BAAI/bge-small-en-v1.5")
        self.logger = get_logger(__name__)
        # Default embedding dimensions and providers
        self.default_embedding_dimension_for_summary = 1536
        self.default_embedding_provider_for_summary = "openai"
        self.default_embedding_dimension_for_content = 1536
        self.default_embedding_provider_for_content = "openai"

    async def get_client(self):
        return await prisma_singleton.get_client()

    def get_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small",
        dimension: Optional[int] = 1536,
        provider: str = "openai",
    ):
        if provider == "openai":
            try:
                MAX_TOKENS = 7000
                tokens = self.tokenizer.encode(text)
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
                self.logger.error(f"Error getting embedding: {e}", exc_info=True)
                raise e
        else:
            return list(self.text_embedding_model.embed(text))

    async def check_if_link_exists(self, link: str, repo: str):
        try:
            dbops = DbOps(await self.get_client())
            return await dbops.check_if_url_exists_in_repo(link, repo)
        except Exception as e:
            self.logger.error(f"Error checking if link exists: {e}", exc_info=True)
            raise e
