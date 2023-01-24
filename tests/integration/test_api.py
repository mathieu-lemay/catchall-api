from typing import Union

import pytest
from starlette.testclient import TestClient

from catchall_api.api import app


@pytest.fixture()
async def api_client() -> TestClient:
    return TestClient(app)


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
async def test_get(api_client: TestClient, path: str, expected_path: str) -> None:
    resp = api_client.get(path)
    assert resp.ok
    assert resp.json() == {
        "path": expected_path,
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "connection": "keep-alive",
            "host": "testserver",
            "user-agent": "testclient",
        },
    }


async def test_get_with_params(api_client: TestClient) -> None:
    resp = api_client.get("/", params={"foo": "bar"})
    assert resp.ok
    assert resp.json() == {
        "path": "/",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "connection": "keep-alive",
            "host": "testserver",
            "user-agent": "testclient",
        },
        "query_params": {"foo": "bar"},
    }


async def test_post_root_json_body(api_client: TestClient) -> None:
    resp = api_client.post("/", json={"foo": "bar"})
    assert resp.ok
    assert resp.json() == {
        "path": "/",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "connection": "keep-alive",
            "content-type": "application/json",
            "content-length": "14",
            "host": "testserver",
            "user-agent": "testclient",
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
async def test_post_root_non_json_body(api_client: TestClient, data: Union[str, bytes], expected: str) -> None:
    resp = api_client.post("/", data=data)
    assert resp.ok
    assert resp.json() == {
        "path": "/",
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "connection": "keep-alive",
            "content-length": str(len(data)),
            "host": "testserver",
            "user-agent": "testclient",
        },
        "body": {"raw": expected},
    }
