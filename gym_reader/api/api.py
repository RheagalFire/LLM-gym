from fastapi import FastAPI
from gym_reader.settings import get_settings, initialize_dspy_with_configs
from gym_reader.api.middlewares import ALL_MIDDLEWARES
from gym_reader.api.routes import git_sync, keyword_search, contextual_chat

cfg = get_settings()
initialize_dspy_with_configs()
app = FastAPI(middleware=ALL_MIDDLEWARES)


@app.get("/api/health")
async def health():
    return {
        "status": "OK",
        "app_name": cfg.APP_NAME,
        "environment": cfg.ENVIRONMENT,
    }


app.include_router(git_sync.router)
app.include_router(keyword_search.router)
app.include_router(contextual_chat.router)
