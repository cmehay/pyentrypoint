FROM python:3

ENV POETRY_VIRTUALENVS_CREATE=false

ADD . /tmp/

RUN cd /tmp && \
    pip install --upgrade pip poetry && \
    poetry install --no-dev && \
    rm -rf *

ONBUILD ADD entrypoint-config.yml .

ENTRYPOINT ["pyentrypoint"]
