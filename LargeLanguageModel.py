import os
import chromadb
import openai
import json
from bs4 import BeautifulSoup
from google import genai

# Configuration paths
CONFIG_FILE = "config.json"

# Load configuration
with open(CONFIG_FILE, 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

PROMPT_IMPROVEMENT = config["prompt_improvement"]
LLM_PROMPT_TEMPLATE = config["llm_prompt_template"]

# Configuración
CHROMA_DB_FOLDER = "chromadb_store_en"
OPENAI_MODEL = "text-embedding-3-small"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MAX_CALLS = 100000
MAX_TOKENS = 16000
call_count = 0

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# URLs for Gemini API
GEMINI_LLM_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"


if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Set the OPENAI_API_KEY environment variable.")


if not GEMINI_API_KEY:
    raise ValueError("No Gemini API key found. Set the GEMINI_API_KEY environment variable.")


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


def improve_user_prompt(user_prompt):
    # Generate query embedding
    query_embedding = get_openai_embedding(user_prompt)
    if not query_embedding:
        print("Error generating embedding for query.")
        return

    # Query ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=6
    )

    info = ""
    for idx, metadata in enumerate(results["metadatas"][0]):
        sentence = results["metadatas"][0][idx]['sentence']
        info += f"- {sentence}\n"

    prompt = PROMPT_IMPROVEMENT.format(user_query=user_prompt, current_embeddings=info)

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return response.text


# Interactive search
def interactive_query():
    user_query = input("Enter your question (in English): ")

    # Improve user query using LLM
    improved_query = improve_user_prompt(user_query)

    # Generate query embedding
    query_embedding = get_openai_embedding(improved_query)
    if not query_embedding:
        print("Error generating embedding for query.")
        return

    # Query ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=6
    )

    if not results["ids"] or not results["ids"][0]:
        print("No relevant info found.")
        return

    # Build context information
    info = ""
    for idx, metadata in enumerate(results["metadatas"][0]):
        sentence = results["metadatas"][0][idx]['sentence']
        info += f"- {sentence}\n"

    # Build LLM prompt
    prompt = LLM_PROMPT_TEMPLATE.format(user_query=improved_query, info=info)
    prompt_marker = "Short answer in English:"

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )

    clean_response = extract_response(response.text, prompt_marker)
    print("\nAnswer from LLM:\n")
    print(response.text)


if __name__ == "__main__":
    while True:
        interactive_query()