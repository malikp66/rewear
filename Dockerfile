# Stage 1: Build Python dependencies
FROM python:3.9-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# Stage 2: Final image
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies including nginx
RUN apt-get update && apt-get install -y \
    nginx \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy python wheels from builder
COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Copy custom nginx config
COPY ./nginx/default.conf /etc/nginx/sites-available/default

# Copy entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port (yang akan digunakan Railway)
EXPOSE 8000

CMD ["/entrypoint.sh"]
