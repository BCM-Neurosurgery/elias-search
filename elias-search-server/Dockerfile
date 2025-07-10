# syntax=docker/dockerfile:1.4

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential \
    git \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Add GitHub.com to known_hosts to avoid SSH prompt
RUN mkdir ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts


WORKDIR /app

COPY requirements.txt ./
RUN --mount=type=ssh \
pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]