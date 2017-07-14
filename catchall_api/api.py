import base64
import json
import logging
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Request

from . import settings

JsonDict = dict[str, Any]

app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("{path:path}")
@app.post("{path:path}")
async def root(request: Request, path: str) -> JsonDict:
    path = path or "/"

    if request.headers.get("Content-Type") == "application/json":
        body = await request.json()
    elif int(request.headers.get("Content-Length", 0)) > 0:
        body = base64.b64encode(await request.body()).decode()
    else:
        body = None

    resp = {
        "path": path,
        "headers": dict(request.headers),
    }

    if request.query_params:
        resp["query_params"] = dict(request.query_params)

    if body:
        resp["body"] = body

    _log_response(resp)

    return resp


def _log_response(resp: JsonDict) -> None:
    serialized_resp = json.dumps(resp, indent=2, sort_keys=True)

    print(serialized_resp)

    if settings.log_to_file:
        with open(f"/output/{datetime.now().isoformat()}.json", "w") as f:
            print(serialized_resp, file=f)


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
