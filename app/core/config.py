from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    AES_PASSPHRASE: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    ENCRYPTION_ENABLED: bool = True
    DEBUG: bool = False

    ENCRYPTION_EXCLUDED_PATHS: list[str] = [
        "/docs",
        "/openapi.json",
        "/auth/login",
        "/dev_test/encrypt",
        "/dev_test/decrypt",
    ]

    model_config = {
        "env_file": ".env",
        "extra": "allow",
    }


settings = Settings()
