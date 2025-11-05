FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Poetry
RUN pip install poetry


# Instalar dependências
RUN poetry install --no-root

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 8000


# Comando para executar a aplicação
CMD ["poetry", "run","uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]