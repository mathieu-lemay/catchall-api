FROM acidrain/python-poetry:3.10-alpine as builder
ENV POETRY_NO_INTERACTION=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONDONTWRITEBYTECODE=nopyc
WORKDIR /app

COPY pyproject.toml \
    poetry.lock \
    /app/

RUN set -eu; \
    poetry install --no-root;


FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=true \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

COPY entrypoint.sh /usr/local/bin
COPY --from=builder /app/.venv /app/.venv
COPY catchall_api /app/catchall_api

EXPOSE 8080

ENTRYPOINT ["entrypoint.sh"]
