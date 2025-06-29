# backend/Dockerfile

# Start from a slim, official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed by psycopg2 (the PostgreSQL driver)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy just the requirements file first to leverage Docker's layer caching
COPY ./requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your backend application code into the container
COPY . .

# The command to run your API server when the container starts.
# This example is for FastAPI.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]