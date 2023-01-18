# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY ./django_prototype /code/django_prototype
COPY ./arise_prototype /code/arise_prototype/arise_prototype
COPY setup.py /code/arise_prototype/
RUN pip install ./arise_prototype