from pydantic import BaseSettings, PostgresDsn
from enum import Enum


class Env(str, Enum):
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


class Settings(BaseSettings):
    DATABASE_URL: PostgresDsn
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20
    GOOGLE_OAUTH_CLIENT_ID: str
    GOOGLE_OAUTH_CLIENT_SECRET: str
    APP_SECRET: str
    ENV: Env = Env.DEV

    @property
    def show_docs(self):
        return self.ENV != "prod"

    class Config:
        env_file = ".env"


settings = Settings()
