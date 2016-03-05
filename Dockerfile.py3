# Testing with python 3

FROM python:3

RUN pip3 install pytest twiggy six pyyaml jinja2

ENV PYTHONPATH /opt/

ADD tests/test_template.yml.tpl /tmp/test_template.yml

WORKDIR /opt/tests

ENV SECRET nothing

CMD ["py.test", "-s", "."]
