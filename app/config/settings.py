"""配置管理"""

from enum import Enum
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class Settings(BaseSettings):
    app_name: str = "Kiki Agent"
    app_version: str = "0.1.0"
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8000
    api_prefix: str = "/api/v1"
    cors_allow_origins: list[str] = ["*"]

    llm_provider: Literal["openai", "dashscope"] = "dashscope"
    llm_model: str = "qwen-turbo"
    llm_temperature: float = 0.7

    dashscope_api_key: str | None = None
    openai_api_key: str | None = None

    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60 * 24

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    model_config = SettingsConfigDict(
        env_prefix="kiki_",
        case_sensitive=False,
        extra="ignore",
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
