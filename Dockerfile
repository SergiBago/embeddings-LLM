FROM python:3.11-slim

WORKDIR /app

COPY backend /app/backend
COPY frontend /app/frontend

COPY requirements.txt .

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN mkdir /app/data
RUN mkdir /app/config

# Instalar wget y unzip para poder descargar y descomprimir la BD de google drive
RUN apt-get update && apt-get install -y wget unzip

RUN pip install --upgrade pip && pip install --no-cache-dir --timeout 60 -r requirements.txt

EXPOSE 8080

CMD ["/app/entrypoint.sh"]