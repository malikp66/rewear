#!/bin/sh

echo "Applying database migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn be.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 8 \
  --threads 4 \
  --timeout 60 \
  --worker-class gthread \
  --log-level info \
  --access-logfile -