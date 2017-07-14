#! /bin/sh

uvicorn --host "${CATCHALL_API_HOST:-0.0.0.0}" --port "${CATCHALL_API_PORT:-8080}" "catchall_api.api:app" "$@"
