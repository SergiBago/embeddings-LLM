import os
import chromadb
import markdown
import json
import re
from fastapi import FastAPI, Query
from sentence_transformers import SentenceTransformer
from typing import List

# Configuración
DATA_FOLDER = "markdown_files"
CHROMA_DB_FOLDER = "chromadb_store"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Inicializar el modelo de embeddings
model = SentenceTransformer(EMBEDDING_MODEL)

# Inicializar ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_FOLDER)
collection = chroma_client.get_or_create_collection(name="markdown_docs")


# Función para dividir el texto en oraciones
def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


# Procesar archivos Markdown en todas las subcarpetas
def process_markdown_files():
    for root, _, files in os.walk(DATA_FOLDER):
        for filename in files:
            if filename.endswith(".md"):
                filepath = os.path.join(root, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Convertir Markdown a texto plano
                text = markdown.markdown(content)

                # Dividir el texto en oraciones
                sentences = split_into_sentences(text)

                # Generar embeddings y guardarlos en ChromaDB
                relative_path = os.path.relpath(filepath, DATA_FOLDER)
                for idx, sentence in enumerate(sentences):
                    embedding = model.encode(sentence).tolist()
                    sentence_id = f"{relative_path}_sentence{idx}"
                    collection.add(
                        ids=[sentence_id],
                        embeddings=[embedding],
                        metadatas=[{
                            "filename": relative_path,
                            "sentence": sentence,
                            "sentence_index": idx
                        }]
                    )


# Cargar los documentos si no están indexados aún
if len(collection.get()['ids']) == 0:
    process_markdown_files()

# Crear API con FastAPI
app = FastAPI()


@app.get("/search")
def search(query: str = Query(..., title="Search query")):
    # Generar embedding de la consulta
    query_embedding = model.encode(query).tolist()

    # Buscar en ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1
    )

    if results["ids"]:
        best_match = results["metadatas"][0][0]
        return {
            "filename": best_match["filename"],
            "sentence": best_match["sentence"],
            "sentence_index": best_match["sentence_index"]
        }
    else:
        return {"message": "No matching content found"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
