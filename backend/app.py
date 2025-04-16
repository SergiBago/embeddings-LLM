from flask import Flask, request, jsonify, send_from_directory, Response
from LargeLanguageModel import *
from extractWebInfo.extractWebInfo import extractWebInfo
import os
from flask_cors import CORS

app = Flask(__name__, static_folder="../frontend", static_url_path="")

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

    res = extractWebInfo(url)
    return res



if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
