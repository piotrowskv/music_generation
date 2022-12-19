FROM python:3.10

WORKDIR /code/backend

COPY ./midi /code/midi
COPY ./models /code/models
COPY ./backend /code/backend

RUN pip install pipenv
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

EXPOSE 80

CMD ["pipenv", "run", "hypercorn", "app.app", "--bind", "0.0.0.0:80"]
