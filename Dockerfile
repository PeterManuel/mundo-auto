FROM python:3.12-slim

WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
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

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads/avatars uploads/products static/images/products

# Create start script
RUN echo '#!/bin/sh\n\
\n\
# Handle DATABASE_URL if provided, otherwise construct from components\n\
if [ -z "$DATABASE_URL" ]; then\n\
    export DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}:${POSTGRES_PORT:-5432}/${POSTGRES_DB}"\n\
fi\n\
\n\
# Run migrations\n\
poetry run alembic upgrade head\n\
\n\
# Start the application\n\
poetry run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Command to run the start script
CMD ["/app/start.sh"]

