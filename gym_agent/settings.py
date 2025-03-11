from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Environment(str, Enum):
    Production = "PROD"
    Development = "DEV"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    ENVIRONMENT: Environment = Environment.Development
    OPENAI_API_KEY: str = ""
    APP_NAME: str = "gym_agent"
    MEILISEARCH_URL: str = "http://localhost:7700"
    MEILISEARCH_MASTER_KEY: str = "aSampleMasterKey"
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_PORT: Optional[int] = None
    TAVILY_API_KEY: str = ""
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    # LangGraph settings
    DEFAULT_MODEL: str = "gpt-4o"
    DEFAULT_TEMPERATURE: float = 0.0
    DEFAULT_MAX_TOKENS: int = 4096

    def is_dev(self):
        return self.ENVIRONMENT == Environment.Development

    def is_prod(self):
        return self.ENVIRONMENT == Environment.Production


def get_settings():
    return Settings()
