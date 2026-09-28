from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "SMI Index Review APIs"
    debug: bool = False
    log_level: str = "INFO"
    output_path: Path = Path("output/smi_review.json")
    api_version: str = "0.0.1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
