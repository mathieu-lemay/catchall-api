DOCKER_IMAGE := "acidrain/catchall-api"

run:
    poetry run ./entrypoint.sh --reload

lint:
    pre-commit run --all-files

test:
    poetry run pytest --verbosity=1 --cov --cov-append \
        --cov-report term-missing --cov-fail-under=100

install:
    poetry install --sync

update: _poetry_lock install

docker-build:
    docker build --tag "{{ DOCKER_IMAGE }}:$(git describe --always HEAD)" .

docker-push: docker-build
    docker push "{{ DOCKER_IMAGE }}:$(git describe --always HEAD)"

@docker-tag:
    git describe --always HEAD

_poetry_lock:
    poetry update --lock
