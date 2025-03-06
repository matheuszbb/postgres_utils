FROM python:3.13.2-alpine3.21
LABEL maintainer="byematheus@gmail.com"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ="America/Sao_Paulo"

# Copia a pasta "postgres_utils" para dentro do container.
COPY postgres_utils /postgres_utils

# Entra na pasta postgres_utils no container
WORKDIR /postgres_utils

# RUN executa comandos em um shell dentro do container para construir a imagem.
RUN apk update && \
  apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/edge/main postgresql17-client && \
  python -m venv /venv && \
  /venv/bin/pip install --upgrade pip && \
  /venv/bin/pip install psycopg2-binary && \
  adduser --disabled-password --no-create-home duser && \
  chown -R duser:duser /venv

# Adiciona a pasta scripts e venv/bin no $PATH do container.
ENV PATH="/scripts:/venv/bin:$PATH"

# Muda o usuário para duser
USER duser