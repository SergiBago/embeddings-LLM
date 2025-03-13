import os
import chromadb
import openai
import requests
from bs4 import BeautifulSoup

# Configuración
CHROMA_DB_FOLDER = "chromadb_store"
OPENAI_MODEL = "text-embedding-3-small"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_MODEL_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

MAX_CALLS = 100000
MAX_TOKENS = 16000
call_count = 0

if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Set the OPENAI_API_KEY environment variable.")

if not HUGGINGFACE_API_KEY:
    raise ValueError("No Hugging Face API key found. Set the HUGGINGFACE_API_KEY environment variable.")

headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# Inicializar ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_FOLDER)
collection = chroma_client.get_or_create_collection(name="markdown_docs")

# Configurar cliente OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text()

def split_large_text(text, max_tokens=MAX_TOKENS):
    if len(text) <= max_tokens:
        return [text]
    mid = len(text) // 2
    left_part = split_large_text(text[:mid], max_tokens)
    right_part = split_large_text(text[mid:], max_tokens)
    return left_part + right_part

def get_openai_embedding(text):
    global call_count
    if call_count >= MAX_CALLS:
        raise RuntimeError("Límite de llamadas a OpenAI alcanzado")

    try:
        text_chunks = split_large_text(text)
        embeddings = []

        for chunk in text_chunks:
            response = client.embeddings.create(input=[chunk], model=OPENAI_MODEL)
            call_count += 1
            embeddings.append(response.data[0].embedding)

        return embeddings[0]
    except openai.BadRequestError as e:
        print(f"Error en OpenAI API: {e}")
        return None

def extract_response(full_response, prompt_marker):
    if prompt_marker in full_response:
        return full_response.split(prompt_marker)[-1].strip()
    return full_response.strip()



# Búsqueda interactiva por terminal
def interactive_query():
    user_query = input("Introdueix la teva pregunta: ")


    # Generar embedding de la consulta con OpenAI
    query_embedding = get_openai_embedding(user_query)
    if not query_embedding:
        return {"message": "Error generating embedding for query."}

    # Buscar en ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=5
    )

    if not results["ids"] or not results["ids"][0]:
        print("No s'ha trobat contingut relevant.")
        return

    # Construir el prompt para el LLM
    info = ""
    for idx, metadata in enumerate(results["metadatas"][0]):
        sentence = metadata = results["metadatas"][0][idx]['sentence']
        info += f"- {sentence})\n"

    prompt = f"""Respon de manera breu, directa i exclusivament en català a la pregunta següent, basant-te en la informació proporcionada:

    Pregunta: '{user_query}'

    Informació proporcionada:
    '{info}'
    """

    prompt_marker = "Resposta curta en català:"

    prompt += prompt_marker

    # Enviar prompt al modelo de Hugging Face para obtener respuesta inmediata
    llm_response = requests.post(HUGGINGFACE_MODEL_URL, headers=headers, json={"inputs": prompt})

    if llm_response.status_code == 200:
        response_json = llm_response.json()
        resposta_completa = response_json[0]['generated_text']
        resposta_net = extract_response(resposta_completa, prompt_marker)
        print("\nResposta del model LLM:\n")
        print(resposta_net)
    else:
        print("Error al obtener resposta del model LLM.")

if __name__ == "__main__":
    while True:
        interactive_query()