#!/bin/bash

echo "⏳ Waiting for scraper to complete..."
while [ ! -f ./web_markdowns/done.flag ]; do
  sleep 1
done

echo "✅ Detected done.flag. Running embedding processor..."
python createEmbeddingsDb.py
