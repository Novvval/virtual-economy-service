from typing import Optional

from celery.schedules import crontab
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None

    secret_key: str = "your-secret-key-here"
    debug: bool = False
    max_balance_update_amount: int = 10000

    celery_beat_schedule: dict = {
        "clear_inventory_cache": {
            "task": "src.infrastructure.tasks.clear_inventory_cache_task",
            "schedule": crontab(hour=2),
        },
    }
    active_test: bool = False

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
