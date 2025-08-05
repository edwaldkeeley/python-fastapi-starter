from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    database_url: str
    jwt_secret: str

    MINIO_ENDPOINT: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_BUCKET: str

    class Config:
        env_file = ".env"
        extra = "forbid"


settings: Settings = Settings()
