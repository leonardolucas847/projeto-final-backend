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

FROM python:3.11-slim

# Evita gerar arquivos .pyc e força saída direta no terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências do sistema necessárias para psycopg2 e imagens
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Coleta arquivos estáticos para o Swagger carregar CSS/JS
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Executa as migrações no banco e inicia o servidor com Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn config.wsgi:projeto-final --bind 0.0.0.0:8000"]