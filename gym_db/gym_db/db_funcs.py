import prisma
from prisma.models import enums, DocumentRecords
from typing import Optional, List


class DbOps:
    def __init__(self, prisma_client: prisma.Prisma):
        self.prisma_client = prisma_client

    async def upsert_document(
        self, url: str, type: enums.DocumentType, repo: str
    ) -> Optional[DocumentRecords]:
        document_record = await self.prisma_client.documentrecords.create(
            data={
                "url": url,
                "type": type,
                "repo": repo,
            }
        )
        return document_record

    async def update_document_status_by_uuid(
        self, uuid: str, is_indexed: bool
    ) -> Optional[DocumentRecords]:
        document_record = await self.prisma_client.documentrecords.update(
            where={"uuid": uuid}, data={"is_indexed": is_indexed}
        )
        return document_record

    async def update_document_deleted_status_by_uuid(
        self, uuid: str, is_deleted: bool
    ) -> Optional[DocumentRecords]:
        document_record = await self.prisma_client.documentrecords.update(
            where={"uuid": uuid}, data={"is_deleted": is_deleted}
        )
        return document_record

    async def get_document_record_by_url(self, url: str) -> Optional[DocumentRecords]:
        document_record = await self.prisma_client.documentrecords.find_unique(
            where={"url": url}
        )
        return document_record

    async def get_documents_to_index(self) -> List[DocumentRecords]:
        documents = await self.prisma_client.documentrecords.find_many(
            where={"is_indexed": False, "is_deleted": False}
        )
        return documents

    async def check_if_url_exists_in_repo(self, url: str, repo: str) -> bool:
        document_record = await self.prisma_client.documentrecords.find_first(
            where={"url": url, "repo": repo}
        )
        return document_record is not None
