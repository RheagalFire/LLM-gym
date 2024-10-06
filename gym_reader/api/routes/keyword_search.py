from fastapi import APIRouter, Request, HTTPException
from typing import Any
from gym_reader.logger import get_logger
from gym_reader.clients.meilisearch_client import meilisearch_client
from fastapi.responses import JSONResponse

log = get_logger(__name__)
router = APIRouter()


@router.get("/api/v1/keyword_search")
async def keyword_search(request: Request, keyword: str, collection_name: str) -> Any:
    try:
        log.debug(request.headers)
        all_attributes = meilisearch_client.index(collection_name).search(keyword)
        return JSONResponse(content=all_attributes)
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
