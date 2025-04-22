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
    'https://drive.usercontent.google.com/download?id=10Qj_WlAJhQ2DzWsmLt_PnmIamebL_rkt&export=download&authuser=0&confirm=t&uuid=91ef7bd7-5a0b-4a47-ab27-e92001ccbd9e&at=APcmpozeQz65CzgOyOKkvnaCVqTM:1745307678676' \
    -O /app/data/temp.zip

  echo "[Entrypoint] Descomprimiendo base de datos..."
  unzip /app/data/temp.zip -d /app/data
  rm /app/data/temp.zip

  apt-get remove -y wget unzip && apt-get autoremove -y && apt-get clean

  echo "[Entrypoint] Descarga y descompresión completadas."
else
  echo "[Entrypoint] Base de datos ya presente. No se descargará nada."
fi

# Finalmente ejecuta la app
exec python3 -u ./backend/app.py