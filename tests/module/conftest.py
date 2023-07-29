import os
from pathlib import Path

import pytest
from _pytest.tmpdir import TempPathFactory


@pytest.fixture(scope="session")
def log_file_directory(tmp_path_factory: TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("log_output")


@pytest.fixture(scope="session")
def docker_compose_file() -> Path:
    return Path(__file__).parent.parent / "docker-compose.yml"


@pytest.fixture(scope="session")
def docker_compose_project_name() -> str:
    return "catchall-api"


@pytest.fixture(scope="session")
def docker_setup(
    docker_setup: str, log_file_directory: Path, tmp_path_factory: TempPathFactory
) -> str:
    env_vars = "".join(
        [
            f"{k}={v}\n"
            for k, v in {
                "USER_ID": os.getuid(),
                "LOG_FILE_DIRECTORY": log_file_directory,
            }.items()
        ]
    )

    tmp_dir = tmp_path_factory.mktemp("env")
    env_file = tmp_dir / "env"
    env_file.write_text(env_vars)

    return f"--env-file {env_file} {docker_setup}"


@pytest.fixture(scope="session")
def docker_cleanup() -> str | None:
    return None
