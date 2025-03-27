import os
import chromadb
import re
import openai
from bs4 import BeautifulSoup
from fastapi import FastAPI, Query

# Configuración
DATA_FOLDER = "./markdown_files/fib_markdown_cat"
CHROMA_DB_FOLDER = "chromadb_store"
OPENAI_MODEL = "text-embedding-3-small"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_CALLS = 1000000
MAX_TOKENS = 16000  # Límite seguro para evitar el error de 8192 tokens
call_count = 0
BASE_URL = "https://fib.upc.edu/"

if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Set the OPENAI_API_KEY environment variable.")

# Inicializar ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_FOLDER)
collection = chroma_client.get_or_create_collection(name="markdown_docs")

# Configurar cliente OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Función para limpiar HTML
def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text()


# Función para contar tokens con OpenAI tokenizer
def count_tokens(text):
    return len(client.tokenize(model=OPENAI_MODEL, input=[text]).data[0].tokens)


# Función para dividir texto en fragmentos de tamaño seguro
def split_large_text(text, max_tokens=MAX_TOKENS):
    if len(text) <= max_tokens:
        return [text]
    mid = len(text) // 2
    left_part = split_large_text(text[:mid], max_tokens)
    right_part = split_large_text(text[mid:], max_tokens)
    return left_part + right_part


# Función para obtener embeddings de OpenAI con manejo de errores
def get_openai_embedding(text):
    global call_count
    if call_count >= MAX_CALLS:
        raise RuntimeError("Límite de llamadas a OpenAI alcanzado")

    try:
        text_chunks = split_large_text(text)
        embeddings = []

        for chunk in text_chunks:
            response = client.embeddings.create(
                input=[chunk],
                model=OPENAI_MODEL
            )
            call_count += 1
            embeddings.append(response.data[0].embedding)

        return embeddings
    except openai.BadRequestError as e:
        print(f"Error en OpenAI API: {e}")
        return None


# Función para dividir el texto en frases
def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


# Crear API con FastAPI
app = FastAPI()


@app.get("/search")
def search(query: str = Query(..., title="Search query")):
    # Generar embedding de la consulta con OpenAI
    query_embedding = get_openai_embedding(query)
    if not query_embedding:
        return {"message": "Error generating embedding for query."}

    # Buscar en ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=5
    )

    if results["ids"]:
        best_match = results["metadatas"][0][0]
        return {
            "filename": best_match["filename"],
            "url": f"{BASE_URL}{best_match['filename'].replace('fib_markdown_cat','').replace(os.sep, '/').replace('//','/').replace('.md','')}",
            "sentence": best_match["sentence"],
            "sentence_index": best_match["sentence_index"]
        }
    else:
        return {"message": "No matching content found"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
