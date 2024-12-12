from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict
import dspy
from typing import Optional


class Environment(str, Enum):
    Production = "PROD"
    Development = "DEV"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    ENVIRONMENT: Environment = Environment.Development
    OPENAI_API_KEY: str = ""
    APP_NAME: str = "gym_reader"
    MEILISEARCH_URL: str = "http://localhost:7700"
    MEILISEARCH_MASTER_KEY: str = "aSampleMasterKey"
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_PORT: Optional[int] = None
    DATABASE_URL: str = ""
    TOKEN_KEY: str = "X-Total-LLM-Tokens"
    PAT_TOKEN: str = ""
    CONFIG_FILE_PATH: str = "gym_reader/config.yaml"
    TAVILY_API_KEY: str = ""
    SPIDER_API_KEY: str = ""
    GITHUB_SECRET_KEY_FOR_WEBHOOK: str = ""
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    DAILY_TOKEN_LIMIT: int = 10000  # Example daily limit
    IP_TOKEN_LIMIT: int = 1000  # Example per-IP limit

    def is_dev(self):
        return self.ENVIRONMENT == Environment.Development

    def is_prod(self):
        return self.ENVIRONMENT == Environment.Production


def get_4o_token_model():
    return dspy.OpenAI(
        model="gpt-4o", api_key=Settings().OPENAI_API_KEY, max_tokens=4096
    )


def initialize_dspy_with_configs(
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    max_tokens: Optional[int] = None,
    set_global: bool = True,
):
    """
    This function initializes dspy with the given model, api_key, and max_tokens.
    It returns the model wrapper object in dspy.
    Args:
        model (str, optional): The model to use. Defaults to "gpt-4o".
        api_key (str, optional): The API key to use. Defaults to the OPENAI_API_KEY from the settings.
        max_tokens (int, optional): The maximum number of tokens to use. Defaults to 3000.
    Returns:
        dspy.OpenAI: The model wrapper object in dspy.
    """
    if model is None:
        model = "gpt-4o"
    if api_key is None:
        api_key = Settings().OPENAI_API_KEY
    if max_tokens is None:
        max_tokens = 3000
    turbo = dspy.OpenAI(
        model=model,
        api_key=api_key,
        max_tokens=max_tokens,
    )
    # disable later , right now setting the model to the global level
    if set_global:
        dspy.settings.configure(lm=turbo)
    # this returns the model wrapper object in dspy
    return turbo


def get_settings():
    return Settings()
