from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    database_url: str
    jwt_secret: str

    class Config:
        env_file = ".env"


settings: Settings = Settings()
