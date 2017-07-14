from typing import Optional

from pydantic import BaseSettings, Field

__project_name__ = "catchall_api"


class Settings(BaseSettings):
    # Binding on all interfaces is fine, we'll be running in docker
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8080
    debug: bool = False
    log_level: str = "INFO"
    log_to_file: bool = False
    log_no_color: Optional[str] = Field(default=None, env="NO_COLOR")

    class Config:
        env_file = ".env"
        env_prefix = "CATCHALL_API_"


settings = Settings()
