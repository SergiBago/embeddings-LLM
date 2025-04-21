#!/bin/bash
set -e

echo "[Entrypoint] Verificando estructura de carpetas..."
mkdir -p /app/data/markdown
mkdir -p /app/data/chromadb_store_en

# Verificamos si la carpeta está vacía antes de descargar
if [ -z "$(ls -A /app/data/chromadb_store_en)" ]; then
  echo "[Entrypoint] No se encontró la base de datos. Descargando..."

  apt-get update && apt-get install -y wget unzip

  wget --no-check-certificate \
    'https://drive.usercontent.google.com/download?id=1_wMgPjWuu8N9z5usKWbRk8MDWWe4SDUW&export=download&authuser=0&confirm=t&uuid=d503a907-1b7d-47f9-8029-f5060cbc374a&at=APcmpoxoK2cy8lqZ_OH_Gtbc3nKN:1745223399018' \
    -O /app/data/temp.zip

  echo "[Entrypoint] Descomprimiendo base de datos..."
  unzip /app/data/temp.zip -d /app/data
  rm /app/data/temp.zip

  apt-get remove -y wget unzip && apt-get autoremove -y && apt-get clean

  echo "[Entrypoint] Descarga y descompresión completadas."
else
  echo "[Entrypoint] Base de datos ya presente. No se descarga nada."
fi

# Finalmente ejecuta la app
exec python3 -u ./backend/app.py
