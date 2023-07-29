from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

__project_name__ = "catchall_api"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="CATCHALL_API_", populate_by_name=True
    )

    log_level: str = "INFO"
    log_no_color: str | None = Field(default=None, validation_alias="NO_COLOR")
    log_to_file: bool = False
    log_file_directory: Path = Path("/output")
