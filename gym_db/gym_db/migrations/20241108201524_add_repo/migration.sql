-- CreateEnum
CREATE TYPE "DocumentType" AS ENUM ('Link', 'Markdown', 'PDF');

-- CreateTable
CREATE TABLE "DocumentRecords" (
    "uuid" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "type" "DocumentType" NOT NULL,
    "repo" TEXT NOT NULL,
    "is_indexed" BOOLEAN NOT NULL DEFAULT false,
    "is_deleted" BOOLEAN NOT NULL DEFAULT false,
    "is_updated" BOOLEAN NOT NULL DEFAULT false,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "DocumentRecords_pkey" PRIMARY KEY ("uuid")
);
