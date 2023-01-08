# music_generation

Piano music generation using machine learning.

You can build and run the whole project having only docker installed with `docker compose up`.

## frontend

[![](https://github.com/piotrowskv/music_generation/workflows/web-ci/badge.svg)](https://github.com/piotrowskv/music_generation/actions)

Stack:

- [React](https://reactjs.org)
- [Typescript](https://www.typescriptlang.org)
- [Tailwind](https://tailwindcss.com)

Deployed at [https://piotrowskv.github.io/music_generation](https://piotrowskv.github.io/music_generation)

### run locally

#### docker

```sh
cd web
docker build -t music_generation-front . # build image
docker run --rm -p 3001:80 music_generation-front # create container
```

#### development

You will only need [node.js 19](https://nodejs.org/en/download/current/). Then cd into `web/`, install dependencies with `npm install`, and run the project with `npm run dev`.

- run tests with `npm run test`
  - run integration tests with `TEST_URL=http://localhost:1234 npm run test` by pointing to the backend server
- fix code with `npm run lint:fix`

## backend

[![](https://github.com/piotrowskv/music_generation/workflows/backend-ci/badge.svg)](https://github.com/piotrowskv/music_generation/actions)

Stack:

- [Python](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLite](https://www.sqlite.org/index.html)
- [redis](https://redis.io/)

Deployed at [https://vps.shilangyu.dev](https://vps.shilangyu.dev/models)

### run locally

#### docker

```sh
docker build -t music_generation-back -f backend.Dockerfile . # build image
docker run --rm -p 3000:80 music_generation-back # create container
```

#### development

You will need [Python 3.10](https://nodejs.org/en/download/current/) and [Pipenv](https://pipenv.pypa.io). You will also need a local instance of a redis server (controlled by the env variables `REDIS_{HOSTNAME,PORT}`), you can also spin up a quick redis instance with docker: `docker run -p 6379:6379 -it redis/redis-stack:latest`. Then cd into `backend/`, install dependencies with `pipenv install`, and run the project with `pipenv run python main.py`.

- run tests with `pipenv run pytest`
- check types with `pipenv run mypy main.py --disallow-untyped-defs`
- check code style with `pipenv run autopep8 --diff --recursive -aaa .` (or apply changes with `pipenv run autopep8 --in-place --recursive -aaa .`)
