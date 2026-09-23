FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render Free tarifida "Shell" bo'lmagani uchun bazani qo'lda tayyorlab
# bo'lmaydi — shuning uchun har bir ishga tushishda avtomatik tekshiriladi
# (scripts/init_production_db.py idempotent: sxema allaqachon bo'lsa o'tkazib
# yuboradi, faqat yo'q bo'lsagina yaratadi). Render/Railway $PORT orqali
# portni beradi.
CMD ["sh", "-c", "python -m scripts.init_production_db && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-4000}"]
