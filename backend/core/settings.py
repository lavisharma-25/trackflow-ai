import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from ai.llm_config import get_provider


BASE_DIR = Path(__file__).resolve().parents[1]

# print(f"BASE_DIR: {BASE_DIR}")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "TrackFlow AI"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-first universal tracker and personal second-brain API"

    APP_ENV: str = "development"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    DEBUG: bool = False

    LLM_PROVIDER: str = "nvidia"


    # ==========================================================================
    # Gemini
    # ==========================================================================
    # GOOGLE_MODEL: str = "gemini-2.5-flash"
    # GOOGLE_API_KEY: str | None = None
    # GOOGLE_CLOUD_PROJECT: str
    # GOOGLE_CLOUD_LOCATION: str = "global"
    # GOOGLE_APPLICATION_CREDENTIALS: str

    # ==========================================================================
    # OPENAI
    # ==========================================================================
    OPENAI_MODEL: str | None = None
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str | None = None

    # ==========================================================================
    # OpenRouter
    # ==========================================================================
    OPENROUTER_MODEL: str = "google/gemma-4-26b-a4b-it:free"
    OPENROUTER_API_KEY: str
    
    # ==========================================================================
    # OpenCode
    # ==========================================================================
    OPENCODE_MODEL: str = "deepseek-v4-flash-free"
    OPENCODE_API_KEY: str | None = None
    OPENCODE_BASE_URL: str | None = None

    # ==========================================================================
    # Groq
    # ==========================================================================
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    GROQ_API_KEY: str | None = None
    GROQ_BASE_URL: str | None = None

    # ==========================================================================
    # Nvidia
    # ==========================================================================
    NVIDIA_MODEL: str | None = None
    NVIDIA_API_KEY: str | None = None
    NVIDIA_BASE_URL: str | None = None

    # ==========================================================================
    # Paths
    # ==========================================================================
    PROJECT_ROOT: Path = BASE_DIR
    STORAGE_DIR: Path = PROJECT_ROOT / "storage"
    LLM_CONFIG_PATH: Path = PROJECT_ROOT / "config" / "llm.providers.json"

    DATABASE_URL: str = (
        f"sqlite:///{(STORAGE_DIR / 'trackflow.db').as_posix()}"
    )

    FRONTEND_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


    def get_llm_config(self, provider_name: str | None = None) -> dict:
        """Resolve an LLM provider and its environment values."""

        config = get_provider(
            provider_name=provider_name or self.LLM_PROVIDER,
            config_path=self.LLM_CONFIG_PATH,
        )["config"]

        llm_config = {}

        for key, value in config.items():
            if key == "display_name":
                llm_config[key] = value
            else:
                llm_config[key] = getattr(self, value, None)

        return llm_config

    # ==========================================================================
    # Directory Management
    # ==========================================================================
    def create_directories(self) -> None:
        """
        Create all required application directories.
        """
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)



@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.create_directories()
    config = settings.get_llm_config()
    print(f"LLM provider config: {config}")
    return settings


settings = get_settings()