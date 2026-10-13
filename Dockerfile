FROM python:3.12-slim

# Evita a criação de arquivos .pyc e garante logs diretos no terminal
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Instala pacotes do sistema necessários para o Pillow e compilação
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala o Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# Copia os arquivos de dependência do Poetry
COPY pyproject.toml poetry.lock* /app/

# Instala as dependências do projeto
RUN poetry install --no-root --no-dev

# Copia todo o código-fonte para o container
COPY . /app/

# Expõe a porta do Django
EXPOSE 8000

# Executa as migrações e inicia o servidor acessível externamente
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]