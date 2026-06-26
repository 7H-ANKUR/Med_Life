from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://dev_user:dev_password@localhost:5432/travel_health"
    redis_url: str = "redis://localhost:6379"

    # Google Maps
    google_maps_api_key: str = ""

    # AI
    ai_provider: str = "openai"  # 'openai' | 'gemini'
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    apify_api_key: str = ""

    # Auth
    jwt_secret: str = "change_this_secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    refresh_token_expire_days: int = 7

    # App
    environment: str = "local"
    allowed_origins: str = "http://localhost:3000"
    sentry_dsn: str = ""

    # Rate Limiting
    rate_limit_ai: str = "10/minute"
    rate_limit_places: str = "30/minute"
    rate_limit_auth: str = "5/minute"

    # Cache TTLs (seconds)
    cache_ttl_places: int = 600
    cache_ttl_fees: int = 86400
    cache_ttl_geocode: int = 604800

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
