from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field

__project_name__ = "catchall_api"


class Settings(BaseSettings):
    log_level: str = "INFO"
    log_no_color: Optional[str] = Field(default=None, env="NO_COLOR")
    log_to_file: bool = False
    log_file_directory: Path = Path("/output")

    uvicorn_log_level = Field(default="INFO", env="UVICORN_LOG_LEVEL")
    uvicorn_no_access_log = Field(default=False, env="UVICORN_NO_ACCESS_LOG")

    class Config:
        env_file = ".env"
        env_prefix = "CATCHALL_API_"
