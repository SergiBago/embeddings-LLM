FROM python:3.11-slim

WORKDIR /app

COPY backend ./backend
COPY frontend ./frontend
RUN mkdir ./data
RUN mkdir ./config
COPY requirements.txt .

COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Instalar wget y unzip para poder descargar y descomprimir la BD de google drive
RUN apt-get update && apt-get install -y wget unzip

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8080

CMD ["/app/entrypoint.sh"]