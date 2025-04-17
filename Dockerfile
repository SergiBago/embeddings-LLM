FROM python:3.11-slim

WORKDIR /app

COPY backend ./backend
COPY frontend ./frontend
COPY chromadb_store_en ./chromadb_store_en
COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8080

CMD [ "python3", "-u", "./backend/app.py" ]