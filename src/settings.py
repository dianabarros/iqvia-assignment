from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    RAW_DB_NAME: str
    RAW_DB_USER: str
    RAW_DB_PASSWORD: str
    RAW_DB_HOST: str
    RAW_DB_PORT: str
    REFINED_DB_NAME: str
    REFINED_DB_USER: str
    REFINED_DB_PASSWORD: str
    REFINED_DB_HOST: str
    REFINED_DB_PORT: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()