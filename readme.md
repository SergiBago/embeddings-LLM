# 🧠 Chatbot Web Scraper

Este proyecto permite procesar y consultar sitios web mediante un chatbot impulsado por IA.

---

## ⚙️ Configuración

Antes de ejecutar el proyecto, rellena las variables necesarias en el archivo `.env`:

```env
OPENAI_API_KEY=tu_clave_openai
GEMINI_API_KEY=tu_clave_gemini
MAX_FILES=30
```

### 📌 Detalles de las variables
OPENAI_API_KEY
Clave para acceder a la API de OpenAI.
👉 Más info: https://openai.com

GEMINI_API_KEY
Clave para la API de Gemini (Google).
👉 Más info: https://ai.google.dev/gemini-api/docs/api-key?hl=es-419

MAX_FILES
Número máximo de archivos que se descargarán y analizarán al hacer scraping de una web.
Útil para evitar procesar sitios demasiado grandes.

---

## 🚀 Ejecución
Una vez configurado el archivo .env, ejecuta:

```
docker compose up --build
```
---

## 🎉 ¡Listo!
Accede a http://localhost:8080 , carga las webs necesarias y empieza a chatear con tu asistente inteligente.