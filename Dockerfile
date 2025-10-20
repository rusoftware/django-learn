FROM python:3.12-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# Dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libffi-dev \
    mariadb-client \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copiar código del proyecto
COPY ./app /code

# Crear carpeta de media
RUN mkdir -p /code/media

# Reemplazar el CMD
CMD ["sh", "/usr/local/bin/wait-for-db.sh", "python", "manage.py", "migrate", "--noinput", "&&", "python", "manage.py", "runserver", "0.0.0.0:8000"]