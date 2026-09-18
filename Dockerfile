FROM python:3.12-slim

# Evita geração de ficheiros .pyc e força saída direta no terminal
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1

# Instala Poetry
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# Copia arquivos de dependência
COPY pyproject.toml poetry.lock* /app/

# Instala dependências via Poetry
RUN poetry install --no-root

COPY . /app/