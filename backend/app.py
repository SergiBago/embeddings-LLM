from flask import Flask, request, jsonify, send_from_directory, Response
from LargeLanguageModel import *
from extractWebInfo.extractWebInfo import extractWebInfo
import os
from flask_cors import CORS
import threading
import uuid

app = Flask(__name__, static_folder="../frontend", static_url_path="")

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

    res = handle_query(user_query)
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
    except Exception as e:
        progress_dict[task_id] = {"status":"error", "text":str(e)}

@app.route("/progress/<task_id>")
def get_progress(task_id):
    data = progress_dict.get(task_id)
    if data is None:
        return jsonify({"status": "not_found", "text": ""})
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
