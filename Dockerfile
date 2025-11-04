# Use Python 3.10 as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    POSTGRES_PORT=5432

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Configure poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-root

# Copy the rest of the application
COPY . .

# Create uploads directory
RUN mkdir -p uploads/avatars uploads/products static/images/products

# Create a script to run the application
RUN echo '#!/bin/sh\n\
if [ -z "$PORT" ]; then\n\
    export PORT=8000\n\
fi\n\
if [ -z "$POSTGRES_PORT" ]; then\n\
    export POSTGRES_PORT=5432\n\
fi\n\
poetry run alembic upgrade head\n\
poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Command to run the start script
CMD ["/app/start.sh"]