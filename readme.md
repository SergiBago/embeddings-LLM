# 🧠 Chatbot Web Scraper

Este proyecto permite procesar y consultar sitios web mediante un chatbot impulsado por IA.

---

## ⚙️ Configuración

### Environment
Antes de ejecutar el proyecto, rellena las variables necesarias en el archivo `.env`:

```env
OPENAI_API_KEY=tu_clave_openai
```

#### Detalles de las variables
OPENAI_API_KEY
Clave para acceder a la API de OpenAI.
👉 Más info: https://openai.com

### Fichero de Configuración
Si quieres, modifica el valor de las variables del fichero `config/config.json`

#### Detalles de las variables
* <b>ignore_langs</b> Lista de idiomas a ignorar. La mayoria de sitios web tienen /ca para catalán, /es para español y /en para ingles. El modelo de embeddings que usamos es capaz de calcular los embeddins en multi idioma, por lo que no es necesario bajar todos los idiomas

* <b>ignore_types</b> Lista de tipos de ficheros a ignorar. Se ignorarán todos los ficheros que acaben en alguna extensión de la lista

* <b>max_files</b> Al hacer el scrapping de forma recursiva, el número de páginas puede ser inmenso. Este parámetro limita la cantidad de páginas a descargar y procesar
---

## 📖 Diccionario

El chatbot usa un diccionario para entender mejor algunos acrónimos, como FIB, ETCS, TFG,... Modificalo para añadir los acrónimos que consideres necesarios. El diccionario es el fichero json en `config/dictionary.json`


---

## 🚀 Ejecución
Una vez configurado el proyecto, ejecuta:

```
docker compose up --build
```
---

## 🎉 ¡Listo!
Accede a http://localhost:8080 y empieza a chatear con tu asistente inteligente.

### Notas:
En la primera start up del container, este se baja una BD que hemos subido a Google Drive y que contiene +10.000 elementos/páginas/pdfs de la web de la FIB, por lo que está listo para responder cualquier pregunta sobre la FIB.

La web está en ingles, pero los datos estan en los tres idiomas, y hemos usado embeddings multiidioma, por lo que se pueden hacer preguntas en cualquier idioma.

Si por alguna razon la BD no se puediera descargar automaticamente descargala manualmente de `https://drive.google.com/file/d/10Qj_WlAJhQ2DzWsmLt_PnmIamebL_rkt/view?usp=sharing`, extrae el fichero zip y guarda la carpeta `chromadb_store_en` carpeta `docker_data`

Si quieres que responda preguntas sobre otra web, inserta la web en el imput correspondiente y dale a 'Scratch Website'

