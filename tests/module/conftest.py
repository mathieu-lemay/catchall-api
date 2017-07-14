from pathlib import Path
from typing import Optional

import pytest


@pytest.fixture(scope="session")
def docker_compose_file() -> Path:
    return Path(__file__).parent.parent / "docker-compose.yml"


@pytest.fixture(scope="session")
def docker_compose_project_name() -> str:
    return "catchall-api"


@pytest.fixture(scope="session")
def docker_cleanup() -> Optional[str]:
    return None
