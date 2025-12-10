import pathlib

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # app
    app_host: str = Field(description="Application host", default="localhost")
    app_port: int = Field(description="Application port", default=8000)
    # redis
    redis_host: str = Field(description="Redis host", default="localhost")
    redis_port: int = Field(description="Redis port", default=6379)
    redis_db: int = Field(description="Redis database number", default=0)

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", extra="ignore")

    # logger
    logging_level: str = Field(description="Logging level", default="DEBUG")


settings = Settings()
