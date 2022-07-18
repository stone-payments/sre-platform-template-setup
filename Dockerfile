FROM python:3.8-alpine

RUN python -m pip install --upgrade wheel

COPY . .

RUN python -m pip install -r requirements.txt

ENTRYPOINT ["/setup.py"]
