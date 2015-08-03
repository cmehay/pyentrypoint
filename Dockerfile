# Docker demo, this doesn't have any purpose but for testing

FROM python:3

ADD docker.py /docker.py

CMD ["python", "/docker.py"]
