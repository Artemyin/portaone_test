FROM python:3.11-alpine

WORKDIR /app

COPY . /app

ENTRYPOINT ["python3", "./statistics_counter.py"]
