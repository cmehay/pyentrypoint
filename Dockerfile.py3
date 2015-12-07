# Testing with python 3

FROM python:3

RUN pip3 install pytest twiggy six pyyaml

ADD python-entrypoint /opt/python-entrypoint/
ADD tests/entrypoint-config.yml /opt/python-entrypoint/

WORKDIR /opt/python-entrypoint/

CMD ["py.test", "-s", "."]
