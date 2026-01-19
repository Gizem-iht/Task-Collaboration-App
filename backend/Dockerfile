# backend/Dockerfile
FROM python:3.12-slim

# Python çıktıları daha temiz olsun
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Çalışma dizini
WORKDIR /app

# 🔹 Postgres gibi paketler (psycopg2 vs.) için sistem bağımlılıkları
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Gereksinimleri kopyala ve kur
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Django için port
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
