#! /bin/sh

CATCHALL_API_HOST="${CATCHALL_API_HOST:-0.0.0.0}"
CATCHALL_API_PORT="${CATCHALL_API_PORT:-8080}"

uvicorn --host "${CATCHALL_API_HOST}" --port "${CATCHALL_API_PORT}" \
    --factory "catchall_api.api:create_app" "$@"
