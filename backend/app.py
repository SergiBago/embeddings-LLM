from flask import Flask, request, jsonify, send_from_directory, session
from LargeLanguageModel import *
from extractWebInfo.extractWebInfo import extractWebInfo
from flask_cors import CORS
import threading
import uuid
from collections import deque

app = Flask(__name__, static_folder="../frontend", static_url_path="")
app.secret_key = "clave_chatbot_dgsi_para_sesiones_456123789"



progress_dict = {}

CORS(app)

@app.route('/')
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/query", methods=["GET", "POST"])
def query():
    if request.method == "POST":
        user_query = request.json.get("query", "")
    else:  # GET
        user_query = request.args.get("query", "")

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

        # Inicializa historial si no existe
    if "chat_history" not in session:
        session["chat_history"] = []

    history = session["chat_history"]
    # Usa deque para comportamiento de cola

    res = handle_query(user_query, history)

    session["chat_history"] = history
    return res


@app.route("/downloadWebsite", methods=["GET", "POST"])
def downloadWebsite():
    url = request.json.get('url', "")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    task_id = str(uuid.uuid4())
    progress_dict[task_id] =  {
        "status": "working",
        "text": "Starting..."
    }

    thread = threading.Thread(target=process_website_task, args=(task_id, url))
    thread.start()

    return jsonify({"task_id": task_id})


def process_website_task(task_id, url):
    try:
        progress_dict[task_id] =  {
        "status": "working",
        "text": "Starting..."
        }
        extractWebInfo(url, task_id, progress_dict)
        progress_dict[task_id]['status'] = "done"
        progress_dict[task_id]['text'] += f"\n✅ Finished scrapping {url}!"

    except Exception as e:
        progress_dict[task_id] = {"status":"error", "text":str(e)}

@app.route("/progress/<task_id>")
def get_progress(task_id):
    data = progress_dict.get(task_id)
    if data is None:
        return jsonify({"status": "not_found", "text": ""})

    #If status is error or finished, remove from progresses
    if data["status"] != "working":
        progress_dict.pop(task_id)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8090)
