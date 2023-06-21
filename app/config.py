from enum import Enum, StrEnum

import openai
from pydantic import BaseSettings, PostgresDsn


class Env(StrEnum):
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


class Settings(BaseSettings):
    """
    The `Settings` class is responsible for managing the application's configuration settings.

    It inherits from the `BaseSettings` class provided by the `pydantic` library.
    """

    DATABASE_URL: PostgresDsn
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20
    GOOGLE_OAUTH_CLIENT_ID: str
    GOOGLE_OAUTH_CLIENT_SECRET: str
    OPENAI_API_KEY: str
    APP_SECRET: str
    ENV: Env = Env.DEV
    PROJECT_NAME: str = "polyglot"

    @property
    def show_docs(self):
        return self.ENV != "prod"

    class Config:
        env_file = ".env"


settings = Settings()

openai.api_key = settings.OPENAI_API_KEY
