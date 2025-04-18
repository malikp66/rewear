#!/bin/sh

echo "Applying database migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
gunicorn be.wsgi:application --bind 127.0.0.1:8001 &

echo "Starting Nginx..."
nginx -g "daemon off;"
