from typing import AsyncGenerator, Union

import httpx
import pytest
from httpx import AsyncClient
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
        except Exception:  # noqa BLE001: Do not catch blind exception: `Exception`
            return False
        else:
            return True

    docker_services.wait_until_responsive(timeout=30.0, pause=0.5, check=_check)
    return url


@pytest.fixture()
async def api_client(api_service_url: str) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(base_url=api_service_url) as client:
        yield client


@pytest.mark.parametrize(
    ("path", "expected_path"),
    [
        ("", "/"),
        ("/", "/"),
        ("api", "/api"),
        ("/api", "/api"),
        ("/api/foobar", "/api/foobar"),
    ],
)
async def test_get(api_client: AsyncClient, api_service_host: str, path: str, expected_path: str) -> None:
    resp = await api_client.get(path)
    resp.raise_for_status()

    assert resp.json() == {
        "path": expected_path,
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "connection": "keep-alive",
            "host": api_service_host,
            "user-agent": f"python-httpx/{httpx.__version__}",
        },
    }


async def test_get_with_params(api_client: AsyncClient, api_service_host: str) -> None:
    resp = await api_client.get("/", params={"foo": "bar"})
    resp.raise_for_status()

    assert resp.json() == {
        "path": "/",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "connection": "keep-alive",
            "host": api_service_host,
            "user-agent": f"python-httpx/{httpx.__version__}",
        },
        "query_params": {"foo": "bar"},
    }


async def test_post_root_json_body(api_client: AsyncClient, api_service_host: str) -> None:
    resp = await api_client.post("/", json={"foo": "bar"})
    resp.raise_for_status()

    assert resp.json() == {
        "path": "/",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "connection": "keep-alive",
            "content-type": "application/json",
            "content-length": "14",
            "host": api_service_host,
            "user-agent": f"python-httpx/{httpx.__version__}",
        },
        "body": {"json": {"foo": "bar"}, "raw": "eyJmb28iOiAiYmFyIn0="},
    }


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ("foobar", "Zm9vYmFy"),
        (b"foobar", "Zm9vYmFy"),
        (
            b"#\xcaK^{0l\xb5\xe0#\x1e\xe2\xac\xe2}\xcb\xc9\xceXS\xac\xc9\xbc`\x1e\xf4,A\x06\xc7\x87]",
            "I8pLXnswbLXgIx7irOJ9y8nOWFOsybxgHvQsQQbHh10=",
        ),
    ],
)
async def test_post_root_non_json_body(
    api_client: AsyncClient,
    api_service_host: str,
    data: Union[str, bytes],
    expected: str,
) -> None:
    resp = await api_client.post("/", content=data)
    resp.raise_for_status()

    assert resp.json() == {
        "path": "/",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "connection": "keep-alive",
            "content-length": str(len(data)),
            "host": api_service_host,
            "user-agent": f"python-httpx/{httpx.__version__}",
        },
        "body": {"raw": expected},
    }
