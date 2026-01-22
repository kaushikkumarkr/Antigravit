import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM Configuration
    LLM_PROVIDER: str = "lmstudio"
    LLM_BASE_URL: str = "http://localhost:1234/v1"
    LLM_MODEL_NAME: str = "local-model"
    GOOGLE_API_KEY: Optional[str] = None

    # Database Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "analytics_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres_password"

    # Application Configuration
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_LOG_LEVEL: str = "INFO"

    # Agent Configuration
    AGENT_MAX_RETRIES: int = 3
    AGENT_TIMEOUT_SECONDS: int = 30
    
    # Computed Properties
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
