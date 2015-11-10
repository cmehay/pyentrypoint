# Testing with python 3

FROM python:3

RUN pip3 install pytest

ADD . /opt/docker-tools/

WORKDIR /opt/docker-tools/

CMD ["py.test", "."]
