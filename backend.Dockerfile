FROM python:3.10

ARG REDIS_HOSTNAME
ENV REDIS_HOSTNAME $REDIS_HOSTNAME
ARG REDIS_PORT
ENV REDIS_PORT $REDIS_PORT

WORKDIR /code/backend

COPY ./midi /code/midi
COPY ./models /code/models
COPY ./backend /code/backend

RUN pip install pipenv
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

EXPOSE 80

ENV PIPENV_DONT_LOAD_ENV 1
CMD ["pipenv", "run", "hypercorn", "app.app", "--bind", "0.0.0.0:80"]
