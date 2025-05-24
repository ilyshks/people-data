# Используем официальный Python-образ
FROM python:3.11-slim-bookworm

# Устанавливаем системные зависимости для PostgreSQL
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    python3-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /people_data

# Копируем зависимости первыми для лучшего кэширования
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы приложения
COPY . .

# Создаем непривилегированного пользователя
RUN useradd -r -u 1001 -g root -m -d /people_data appuser && \
    chown -R appuser:root /people_data
USER appuser

# Настройки окружения
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Запускаем приложение
CMD ["sh", "-c", "flask db upgrade && flask fetch-people && waitress-serve --port=8000 app:app"]