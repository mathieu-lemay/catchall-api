import json
from datetime import datetime
from pathlib import Path
from typing import Union
from uuid import uuid4

import pytest
import time_machine
from _pytest.logging import LogCaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from fastapi import FastAPI
from starlette.testclient import TestClient

from catchall_api import Settings
from catchall_api.api import create_app


@pytest.fixture(scope="session")
def api_settings() -> Settings:
    return Settings()


@pytest.fixture(scope="session")
async def api_app(api_settings: Settings) -> FastAPI:
    return create_app(api_settings)


@pytest.fixture(scope="session")
async def api_client(api_app: FastAPI) -> TestClient:
    return TestClient(api_app)


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
async def test_all_methods_are_supported(api_client: TestClient, method: str) -> None:
    resp = api_client.request(method, "/")
    assert resp.is_success

    if method != "HEAD":
        assert resp.json()["method"] == method


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
async def test_empty_get_returns_basic_data(api_client: TestClient, path: str, expected_path: str) -> None:
    resp = api_client.get(path)

    assert resp.is_success
    assert resp.json() == {
        "method": "GET",
        "path": expected_path,
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "connection": "keep-alive",
            "host": "testserver",
            "user-agent": "testclient",
        },
    }


async def test_all_headers_are_returned(api_client: TestClient) -> None:
    auth = str(uuid4())
    headers = {"Authorization": auth, "X-Extra-Header": "some-value"}
    data = b"abc123"

    resp = api_client.post("/", headers=headers, content=data)

    assert resp.is_success
    assert resp.json()["headers"] == {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "connection": "keep-alive",
        "host": "testserver",
        "user-agent": "testclient",
        "authorization": auth,
        "x-extra-header": "some-value",
        "content-length": str(len(data)),
    }


async def test_query_with_query_params(api_client: TestClient) -> None:
    query_params: dict[str, str | int | list[int | str]] = {
        "str-val": "foo",
        "int-val": 123,
        "str-list": ["aaa", "bbb"],
        "int-list": [1, 2, 3],
    }
    expected = {"str-val": "foo", "int-val": "123", "str-list": ["aaa", "bbb"], "int-list": ["1", "2", "3"]}

    resp = api_client.get("/", params=query_params)

    assert resp.is_success
    assert resp.json()["query_params"] == expected


async def test_json_body_is_returned_in_a_dict_and_as_base64(api_client: TestClient) -> None:
    resp = api_client.post("/", json={"foo": "bar"})
    assert resp.is_success
    assert resp.json()["body"] == {
        "json": {"foo": "bar"},
        "raw": "eyJmb28iOiAiYmFyIn0=",
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
async def test_non_json_body_is_returned_as_base64(
    api_client: TestClient, data: Union[str, bytes], expected: str
) -> None:
    resp = api_client.post("/", content=data)
    assert resp.is_success
    assert resp.json()["body"] == {"raw": expected}


async def test_empty_body_with_bogus_content_length_is_not_returned(api_client: TestClient) -> None:
    resp = api_client.post("/", headers={"Content-Length": "255"})

    assert resp.is_success
    assert "body" not in resp.json()


@pytest.mark.parametrize("should_write_to_file", [True, False])
@time_machine.travel(datetime(2023, 1, 1, 0, 0, 0), tick=False)
async def test_request_data_is_output_to_console_and_file(
    api_settings: Settings,
    api_client: TestClient,
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
    should_write_to_file: bool,
) -> None:
    monkeypatch.setattr(api_settings, "log_to_file", should_write_to_file)
    monkeypatch.setattr(api_settings, "log_file_directory", tmp_path)

    endpoint = str(uuid4())
    path = f"/{endpoint}"

    resp = api_client.post(path, json={"foo": "bar"})

    assert resp.is_success

    expected_response = {
        "body": {"json": {"foo": "bar"}, "raw": "eyJmb28iOiAiYmFyIn0="},
        "headers": {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "connection": "keep-alive",
            "content-length": "14",
            "content-type": "application/json",
            "host": "testserver",
            "user-agent": "testclient",
        },
        "method": "POST",
        "path": path,
    }

    assert f"POST {path}" in caplog.text
    assert json.dumps(expected_response, indent=2, sort_keys=True) in caplog.text

    expected_file_name = f"{datetime.now().isoformat()}-POST--{endpoint}.json"
    expected_file = tmp_path / expected_file_name
    if should_write_to_file:
        assert expected_file.exists()
        file_data = json.loads(expected_file.read_text())

        assert file_data == expected_response
    else:
        assert not expected_file.exists()
