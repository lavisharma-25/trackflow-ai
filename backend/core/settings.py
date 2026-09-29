from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from ai.llm_config import get_provider


BASE_DIR = Path(__file__).resolve().parents[1]


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

    STORAGE_DIR: Path = BASE_DIR / "storage"
    LLM_CONFIG_PATH: Path = BASE_DIR / "config" / "llm.providers.json"

    DATABASE_URL: str = (
        f"sqlite:///{(BASE_DIR / 'storage' / 'trackflow.db').as_posix()}"
    )

    FRONTEND_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    LLM_PROVIDER: str = "openrouter"

    def ensure_dirs(self) -> None:
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)


    def get_llm_provider(
        self,
        provider_name: str | None = None,
    ) -> dict:
        """Resolve an LLM provider and its environment values."""
        return get_provider(
            provider_name=provider_name or self.LLM_PROVIDER,
            config_path=self.LLM_CONFIG_PATH,
        )




@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    settings.get_llm_provider(settings.LLM_PROVIDER)
    return settings


settings = get_settings()