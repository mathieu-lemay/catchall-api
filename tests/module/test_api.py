from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator
from uuid import uuid4

import httpx
import pytest
from httpx import AsyncClient, HTTPError
from pytest_docker.plugin import Services  # type: ignore[import]


@pytest.fixture(scope="session")
def api_service_host(docker_ip: str, docker_services: Services) -> str:
    port = docker_services.port_for("api", 8080)
    return f"{docker_ip}:{port}"


@pytest.fixture(scope="session")
def api_service_url(api_service_host: str, docker_services: Services) -> str:
    url = f"http://{api_service_host}"

    def _check() -> bool:
        try:
            resp = httpx.get(f"{url}")
            resp.raise_for_status()
        except HTTPError:
            return False  # pragma: no cover
        else:
            return True

    docker_services.wait_until_responsive(timeout=10.0, pause=0.5, check=_check)
    return url


@pytest.fixture()
async def api_client(api_service_url: str) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(base_url=api_service_url) as client:
        yield client


@pytest.mark.parametrize(
    "method",
    [
        "DELETE",
        "GET",
        "HEAD",
        "OPTIONS",
        "PATCH",
        "POST",
        "PUT",
        "TRACE",
    ],
)
async def test_all_methods_are_supported(api_client: AsyncClient, method: str) -> None:
    resp = await api_client.request(method, "/")
    assert resp.is_success

    if method != "HEAD":
        assert resp.json()["method"] == method


async def test_all_headers_are_returned(
    api_client: AsyncClient, api_service_host: str, log_file_directory: Path
) -> None:
    auth = str(uuid4())
    headers = {"Authorization": auth, "X-Extra-Header": "some-value"}
    data = b"abc123"

    log_files = set(log_file_directory.glob("*.json"))
    ts_start = datetime.utcnow()

    resp = await api_client.post("/", headers=headers, content=data)

    ts_end = datetime.utcnow()

    assert resp.is_success
    assert resp.json()["headers"] == {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "connection": "keep-alive",
        "host": api_service_host,
        "user-agent": f"python-httpx/{httpx.__version__}",
        "authorization": auth,
        "x-extra-header": "some-value",
        "content-length": str(len(data)),
    }

    new_log_files = list(set(log_file_directory.glob("*.json")) - log_files)
    assert len(new_log_files) == 1

    log_file_name = new_log_files[0].name
    assert log_file_name.endswith("-POST--.json")

    log_file_timestamp = datetime.fromisoformat(log_file_name.split("-POST-")[0])
    assert ts_start <= log_file_timestamp <= ts_end
