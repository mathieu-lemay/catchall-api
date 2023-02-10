import base64
import json
import logging
from collections import Counter
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Optional

from fastapi import Depends, FastAPI, Request

from . import Settings
from .log import configure_loggers

JsonDict = dict[str, Any]

app = FastAPI()
logger = logging.getLogger(__name__)

settings_dependency = Depends(lambda: app.state.settings)


@app.delete("{path:path}")
@app.get("{path:path}")
@app.head("{path:path}")
@app.options("{path:path}")
@app.patch("{path:path}")
@app.post("{path:path}")
@app.put("{path:path}")
@app.trace("{path:path}")
async def root(request: Request, path: str, settings: Settings = settings_dependency) -> JsonDict:
    path = path or "/"

    request_data = {
        "method": request.method,
        "path": path,
        "client": _get_client_info(request),
        "url": _get_url_info(request),
        "headers": dict(request.headers),
    }

    if query_params := _get_query_params(request):
        request_data["query_params"] = query_params

    if body := await _get_body(request):
        request_data["body"] = body

    _log_request_data(request.method, path, request_data, settings.log_to_file, settings.log_file_directory)

    return request_data


def _get_client_info(request: Request) -> Optional[JsonDict]:
    return {
        "remote_ip": request.client.host if request.client else None,
        "port": request.client.port if request.client else None,
    }


def _get_url_info(request: Request) -> Optional[JsonDict]:
    url = request.url
    return {
        "scheme": url.scheme,
        "hostname": url.hostname,
        "port": url.port,
        "path": url.path,
    }


def _get_query_params(request: Request) -> Optional[JsonDict]:
    if not request.query_params:
        return None

    param_keys = Counter([i[0] for i in request.query_params.multi_items()])

    return {
        key: request.query_params.get(key) if count == 1 else request.query_params.getlist(key)
        for key, count in param_keys.items()
    }


async def _get_body(request: Request) -> Optional[JsonDict]:
    if not request.headers.get("Content-Length"):
        return None

    body = {}

    if raw_body := base64.b64encode(await request.body()).decode():
        body["raw"] = raw_body
    else:
        return None

    try:
        json_body = await request.json()
        body["json"] = json_body
    except (JSONDecodeError, UnicodeDecodeError):
        pass  # noqa: S110: `try`-`except`-`pass` detected

    return body


def _log_request_data(method: str, path: str, data: JsonDict, log_to_file: bool, log_file_directory: Path) -> None:
    serialized_request = json.dumps(data, indent=2, sort_keys=True)

    logger.info("%s %s\n%s", method, path, serialized_request)

    if not log_to_file:
        return

    log_file = log_file_directory / f"{datetime.utcnow().isoformat()}-{method}{path.replace('/', '--')}.json"

    log_file.write_text(serialized_request)


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    settings = settings or Settings()

    app.state.settings = settings

    configure_loggers(settings)

    return app
