FROM python:3.12-slim

# Evita a criação de arquivos .pyc, força logs diretos no terminal e configura o Poetry
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

# Instala dependências de sistema necessárias para compiladores, PostgreSQL e tratamento de imagens (Pillow)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala o Poetry
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# Copia os arquivos de especificação de dependências
COPY pyproject.toml poetry.lock* /app/

# Atualiza a trava do lock sem alterar versões e instala as dependências
RUN poetry lock --no-update && poetry install --no-root

# Copia todo o código-fonte da aplicação
COPY . /app/

# Coleta os arquivos estáticos (resolve o visual do Admin do Django e Swagger)
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Aplica as migrações no banco e inicia a aplicação com o Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]