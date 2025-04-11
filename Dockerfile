# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy the project files into the container
COPY .. /app/be

# Install Python dependencies
RUN pip install --upgrade pip

# Set the working directory to the project folder
WORKDIR /app/be

# Collect static files
RUN python manage.py collectstatic --noinput

# Run the script
CMD ["/app/start.sh"]