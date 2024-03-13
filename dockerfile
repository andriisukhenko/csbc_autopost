FROM python:3.11-alpine

ENV APP_HOME /app \
    POETRY_VERSION 1.7.1

WORKDIR $APP_HOME

COPY . .

RUN pip install "poetry==$POETRY_VERSION"

RUN poetry install --no-root

ENTRYPOINT [ "poetry", "run", "python", "app/main.py" ]