import asyncio
from gym_reader.logger import get_logger
from gym_db.gym_db.db_funcs import DbOps
from gym_reader.clients.qdrant_client import qdrant_client
from gym_reader.clients.meilisearch_client import meilisearch_client
from gym_reader.clients.openai_client import openai_client
from gym_reader.clients.prisma_client import prisma_singleton
from gym_reader.agents.extractor_agent import ContentExtractorAgent, PayloadForIndexing
from gym_reader.settings import get_settings
from gym_reader.semantic_search.index import GymIndex
from tqdm import tqdm

log = get_logger(__name__)

settings = get_settings()

extractor_agent = ContentExtractorAgent()
gym_index = GymIndex(qdrant_client, meilisearch_client, openai_client)


async def index_documents():
    prisma_client = await prisma_singleton.get_client()
    dbops = DbOps(prisma_client)
    while True:
        # Fetch documents that are not indexed and not deleted
        documents = await dbops.get_documents_to_index()
        if not documents:
            log.info("No documents to index")
            await asyncio.sleep(5)
            continue
        log.info(f"Indexing {len(documents)} documents")
        for document in tqdm(documents):
            log.info(f"Indexing document: {document.url}")
            try:
                # Index the document
                meta_to_add_to_index: PayloadForIndexing = extractor_agent.forward(
                    document.url
                )
                gym_index.add_to_qdrant_collection(
                    meta_to_add_to_index, collection_name=document.repo
                )
                gym_index.add_to_meilisearch_collection(
                    meta_to_add_to_index, collection_name=document.repo
                )

                # Update the document status to indexed
                await dbops.update_document_status_by_uuid(document.uuid, True)
            except Exception as e:
                log.error(f"Error indexing document {document.url}: {e}", exc_info=True)

        await asyncio.sleep(5)  # Poll every 10 seconds


if __name__ == "__main__":
    asyncio.run(index_documents())
