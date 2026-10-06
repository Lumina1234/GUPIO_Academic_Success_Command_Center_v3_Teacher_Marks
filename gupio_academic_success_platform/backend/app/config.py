from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "GUPIO Academic Success Command Center"
    app_secret_key: str = "change-me"
    database_url: str = "sqlite:///./gupio.db"
    frontend_origins: str = "http://localhost:5173"
    cookie_secure: bool = False
    session_ttl_hours: int = 8
    login_rate_limit: int = 8
    login_rate_window_seconds: int = 300
    demo_password: str = "ChangeMe!23456789"
    demo_seed_enabled: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def frontend_origin_list(self) -> list[str]:
        return [x.strip() for x in self.frontend_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
