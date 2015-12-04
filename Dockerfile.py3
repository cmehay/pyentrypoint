# Testing with python 3

FROM python:3

#RUN pip3 install pytest

ADD python-entrypoint /opt/docker-entrypoint/

WORKDIR /opt/docker-entrypoint/

ENTRYPOINT ["./entrypoint.py"]

CMD ["echo", "ok"]
