FROM python:3.6-alpine

RUN python -m venv venv
RUN pip install --upgrade pip
RUN apk update && apk add libressl-dev postgresql-dev libffi-dev gcc musl-dev python3-dev

COPY requirements.txt requirements.txt
RUN venv/bin/pip install -r requirements.txt

COPY  . .

ENTRYPOINT ["./boot.sh"]