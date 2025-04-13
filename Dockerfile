FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory ke /app/be
WORKDIR /app/be

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt ke direktori kerja saat ini
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy seluruh konten direktori be ke dalam container
COPY . .

# Buat script entrypoint
RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'python manage.py collectstatic --noinput' >> /entrypoint.sh && \
    echo 'gunicorn --bind 0.0.0.0:8000 be.wsgi:application' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Command untuk menjalankan script entrypoint
CMD ["/entrypoint.sh"]