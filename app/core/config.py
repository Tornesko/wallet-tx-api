import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    AES_PASSPHRASE: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    model_config = {
        "env_file": ".env",
        "extra": "allow",
    }


settings = Settings()

ENCRYPTION_ENABLED = os.getenv("ENCRYPTION_ENABLED", "true").lower() == "true"

ENCRYPTION_EXCLUDED_PATHS = [
    "/docs",
    "/openapi.json",
    "/auth/login",
    "/dev_test/encrypt",
    "/dev_test/decrypt",
]
