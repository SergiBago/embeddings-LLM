from flask import Flask, jsonify, request
from utils.scraper_utils import scrape_site
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/scrape": {"origins": "http://localhost:8080"}})

@app.route("/scrape", methods=["POST"])
def scrape():
    url = request.json.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    # Call the scraping function from the scraper module
    result = scrape_site(url)

    with open("/app/web_markdowns/done.flag", "w") as f:
        f.write("done")

    return jsonify({"message": result}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
