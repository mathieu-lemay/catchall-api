DOCKER_IMAGE := "catchall-api"
DOCKER_TAG := "dev"

run:
    poetry run ./entrypoint.sh --reload

install:
    poetry install --sync

update: _poetry_lock install

lint:
    pre-commit run --all-files

test:
    poetry run pytest --verbosity=1 --cov --cov-append \
        --cov-report term-missing --cov-fail-under=100

docker-build:
    docker build --tag "{{ DOCKER_IMAGE }}:{{ DOCKER_TAG }}" .

_poetry_lock:
    poetry update --lock
