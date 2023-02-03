import base64
import json
import logging
from collections import Counter
from datetime import datetime
from json import JSONDecodeError
from typing import Any, Optional

from fastapi import FastAPI, Request

from . import settings

JsonDict = dict[str, Any]

app = FastAPI()
logger = logging.getLogger(__name__)


@app.delete("{path:path}")
@app.get("{path:path}")
@app.head("{path:path}")
@app.options("{path:path}")
@app.patch("{path:path}")
@app.post("{path:path}")
@app.put("{path:path}")
@app.trace("{path:path}")
async def root(request: Request, path: str) -> JsonDict:
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

    _log_request_data(request_data)

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


def _log_request_data(request: JsonDict) -> None:
    serialized_request = json.dumps(request, indent=2, sort_keys=True)

    print(serialized_request)

    if settings.log_to_file:
        with open(f"/{settings.log_to_file_directory}/{datetime.now().isoformat()}.json", "w") as f:
            print(serialized_request, file=f)


def main() -> None:
    import uvicorn

    uvicorn.run(
        "catchall_api.api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()  # pragma: no cover
