FROM python:3.10-slim-bullseye

## Configs (that don't change often)
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PATH /root/.local/bin:$PATH

# Never prompts the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive

WORKDIR /app
CMD poetry run python main.py

## Install Poetry
RUN apt-get -y update; apt-get -y install curl
ARG poetry_version=1.5.1
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=${poetry_version} python3 -
#RUN poetry config experimental.new-installer false

## Install project dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install

## Copy code
COPY main.py main.py
COPY app/ app/
