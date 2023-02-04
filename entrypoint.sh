#! /bin/sh

CATCHALL_API_HOST="${CATCHALL_API_HOST:-0.0.0.0}"
CATCHALL_API_PORT="${CATCHALL_API_PORT:-8080}"
export UVICORN_LOG_LEVEL="${UVICORN_LOG_LEVEL:-error}"
export UVICORN_NO_ACCESS_LOG="${UVICORN_NO_ACCESS_LOG:-1}"

uvicorn --host "${CATCHALL_API_HOST}" --port "${CATCHALL_API_PORT}" \
    --factory "catchall_api.api:create_app" "$@"
