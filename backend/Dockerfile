FROM python:3.10

WORKDIR /code

# install deps
RUN pip install pipenv
COPY ./Pipfile /code/Pipfile
COPY ./Pipfile.lock /code/Pipfile.lock
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

COPY ./app /code/app

EXPOSE 80

CMD ["pipenv", "run", "hypercorn", "app.app", "--bind", "0.0.0.0:80"]
