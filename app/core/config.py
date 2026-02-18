from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Application
    app_name: str = "Zehn Backend"
    app_version: str = "1.0.0"
    access_token_expire_minutes: int = 600
    secret_key: str = "your_secret_key"
    algorithm: str = "HS256"
    rate_limit_max_requests: int = 1000
    rate_limit_window_seconds: int = 600
    gzip_minimum_size: int = 1
    cors_max_age: int = 3600
    allowed_hosts: List[str] = ["*"]

    sentry_dsn: str | None = None
    debug: bool = True
    environment: str = "local"  # production

    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 10080
    jwt_refresh_token_expire_hours: int = 168


    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_pass: str = "ping1234"
    db_name: str = "zehn_arch_backend_db"

    @property
    def database_url_asyncpg(self):
        # postgresql+asyncpg://postgres:postgres@localhost:5432/sa
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def database_url_psycopg(self):
        # DSN
        # postgresql+psycopg://postgres:postgres@localhost:5432/sa
        return f"postgresql+psycopg2://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

    # URLs

    openai_api_key: str = "Your open_ai api-key"

    # MINIO

    minio_endpoint: str = "localhost:9211"
    minio_public_url: str = "http://localhost:9211"
    minio_access_key: str = "your-access-key"
    minio_secret_key: str = "your-secret-key"
    minio_secure: bool = False
    aws_storage_region: str = "us-east-1"
    # minio buckets
    minio_bucket: str = "minio_bucket"

    # redis
    redis_url: str = "redis://localhost:6379"

    # mongo
    mongo_db_name: str = ""
    mongo_uri: str = ""

    # celery
    celery_broker_url: str = "redis://localhost:6379"
    celery_result_backend: str = "redis://localhost:6379"

    # celery sentry
    sentry_dsn_celery: str = ""
    sentry_traces_sample_rate: str = ""
    sentry_profiles_sample_rate: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = Settings()
