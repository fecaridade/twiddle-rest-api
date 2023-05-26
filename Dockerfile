FROM python:3.9

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y libmagic1 && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip

WORKDIR /srv/app

COPY requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY . .
