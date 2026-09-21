from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


def _default_service_account_path() -> Optional[Path]:
    """Find a local service-account file without making it mandatory."""
    credential_dir = BASE_DIR / "model_credentials"
    return next(credential_dir.glob("*.json"), None)


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "TrackFlow AI"
    APP_ENV: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    STORAGE_DIR: Path = BASE_DIR / "src" / "storage"
    LOGS_DIR: Path = BASE_DIR / "LOGS"
    DATABASE_URL: str = f"sqlite:///{(BASE_DIR / 'src' / 'storage' / 'trackflow.db').as_posix()}"
    FRONTEND_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Kept for importing the original spreadsheet prototype safely.
    TRACKERS_DIR: Path = STORAGE_DIR / "trackers"
    REGISTRY_FILE: Path = STORAGE_DIR / "tracker_registry.json"
    SCHEMA_FILE: Path = STORAGE_DIR / "schema_registry.json"

    GEMINI_MODEL_FLASH: str = "gemini-2.5-flash"
    GEMINI_MODEL_LITE: str = "gemini-2.5-flash-lite"
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    LOCATION: str = "global"
    SERVICE_ACCOUNT_PATH: Optional[Path] = _default_service_account_path()

    TMDB_API_KEY: Optional[str] = None
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().casefold()
            if normalized in {"true", "1", "yes", "on", "debug", "development"}:
                return True
            if normalized in {"false", "0", "no", "off", "release", "production"}:
                return False
        return value

    def ensure_dirs(self) -> None:
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        self.TRACKERS_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    def google_credentials(self):
        """Load Vertex credentials lazily, only when the assistant is used."""
        if not self.SERVICE_ACCOUNT_PATH:
            return None

        from google.oauth2 import service_account

        return service_account.Credentials.from_service_account_file(
            str(self.SERVICE_ACCOUNT_PATH),
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

    @property
    def frontend_origins(self) -> list[str]:
        return [origin.strip() for origin in self.FRONTEND_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
