# syntax=docker/dockerfile:1.4

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y git

# Add GitHub.com to known_hosts to avoid SSH prompt
RUN mkdir ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts


WORKDIR /app

COPY requirements.txt ./
RUN --mount=type=ssh \
pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]