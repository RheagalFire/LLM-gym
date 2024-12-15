from fastapi import APIRouter, Request, HTTPException
from gym_reader.logger import get_logger
from gym_reader.data_models import ChatPayload, ResponseModel, Answer
from gym_reader.agents.semantic_answer import ContextAwareAnswerAgent


log = get_logger(__name__)
router = APIRouter()

chat_agent = ContextAwareAnswerAgent()


@router.post("/api/v1/contextual_chat")
async def keyword_search(request: Request, body: ChatPayload) -> ResponseModel:
    try:
        collection_name = body.collection_name
        messages = body.messages
        search_query = messages[-1].content
        request_id = request.state.request_id
        log.debug(f"request_id: {request_id}")
        conversation_history = [message.model_dump() for message in messages[:-1]]
        log.debug("request headers", request.headers)
        chat_object = chat_agent(
            search_query, collection_name, conversation_history, request_id
        )
        log.debug(chat_object.generated_answer)
        log.debug(chat_object.citations)
        return ResponseModel(
            data=Answer(
                role="assistant",
                content=chat_object.generated_answer,
            ),
            meta={"citations": chat_object.citations},
        )
    except Exception as e:
        log.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
