import base64
import json
import logging
from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, Request

from . import settings

JsonDict = dict[str, Any]

app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("{path:path}")
@app.post("{path:path}")
@app.put("{path:path}")
@app.patch("{path:path}")
@app.delete("{path:path}")
async def root(request: Request, path: str) -> JsonDict:
    path = path or "/"

    request_data = {
        "path": path,
        "headers": dict(request.headers),
    }

    if request.query_params:
        request_data["query_params"] = dict(request.query_params)

    if body := await _get_body(request):
        request_data["body"] = body

    _log_request_data(request_data)

    return request_data


async def _get_body(request: Request) -> Optional[JsonDict]:
    if not request.headers.get("Content-Length"):
        return None

    body = {}

    try:
        raw_body = base64.b64encode(await request.body()).decode()
    except Exception:
        raw_body = None

    try:
        json_body = await request.json()
    except Exception:  # noqa: S110
        json_body = None

    if raw_body:
        body["raw"] = raw_body

    if json_body:
        body["json"] = json_body

    return body


def _log_request_data(request: JsonDict) -> None:
    serialized_request = json.dumps(request, indent=2, sort_keys=True)

    print(serialized_request)

    if settings.log_to_file:
        with open(f"/output/{datetime.now().isoformat()}.json", "w") as f:
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
    main()
