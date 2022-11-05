# music_generation

Piano music generation using machine learning

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
docker build -t music-front . # build image
docker run --rm -p 3001:80 music-front # create container
```

#### development

You will only need [node.js 18](https://nodejs.org/en/download/current/). Then cd into `web/` and run the project with `npm run dev`.

- run tests with `npm run test`
  - run integration tests with `TEST_URL=http://localhost:1234 npm run test` by pointing to the backend server
- fix code with `npm run lint:fix`
