FROM python:3.8-alpine

RUN python -m pip install --upgrade pipenv wheel

COPY . .

RUN pipenv install --deploy


ENTRYPOINT ["/entrypoint.sh"]
