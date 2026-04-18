from flask import Flask, jsonify, request, render_template
import os
from engine import sync_trades, load_db, save_db

app = Flask(__name__)

UPLOAD_PATH = "uploaded.xlsx"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/trades")
def get_trades():
    return jsonify(load_db())

@app.route("/sync", methods=["POST"])
def sync():
    data = sync_trades()
    return jsonify(data)

@app.route("/save", methods=["POST"])
def save():
    updated = request.json
    save_db(updated)
    return jsonify({"status": "saved"})

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Save uploaded file
    if os.path.exists(UPLOAD_PATH):
        os.remove(UPLOAD_PATH)

    file.save(UPLOAD_PATH)
    
    # Tell engine to use this file
    import engine
    engine.EXCEL_FILE = UPLOAD_PATH

    # Re-sync trades
    data = sync_trades()

    return jsonify({"status": "success", "trades": data})

import os

    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=port)
