#選擇基礎環境
FROM python:3.11-slim

#設定工作目錄
WORKDIR /app

#產出的套件清單複製
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]