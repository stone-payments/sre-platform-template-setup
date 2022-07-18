FROM python:3.8-alpine

RUN python -m pip install --upgrade pipenv wheel

COPY . .

RUN pipenv install --deploy

ENTRYPOINT ["pipenv", "run", "python", "setup.py"]
