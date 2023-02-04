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
        "headers": dict(request.headers),
    }

    if query_params := await _get_query_params(request):
        request_data["query_params"] = query_params

    if body := await _get_body(request):
        request_data["body"] = body

    _log_request_data(request_data, settings.log_to_file, settings.log_file_directory)

    return request_data


async def _get_query_params(request: Request) -> Optional[JsonDict]:
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


def _log_request_data(request: JsonDict, log_to_file: bool = True, log_file_directory: Optional[Path] = None) -> None:
    serialized_request = json.dumps(request, indent=2, sort_keys=True)

    print(serialized_request)

    if log_to_file:
        with open(f"/{log_file_directory}/{datetime.now().isoformat()}.json", "w") as f:
            print(serialized_request, file=f)


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    settings = settings or Settings()

    app.state.settings = settings

    configure_loggers(settings)

    return app
