import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS module
from datetime import datetime, timedelta
from google.cloud import firestore, storage
from google.oauth2 import service_account
from typing import List
from utils import firebase_format_date, current_date
from llm_functions import answer_question
from gcloud_helper import get_prefs
from batcher import card_pref

app = Flask(__name__)
CORS(app)
# Set the logging level and handler to send logs to stdout
logging.basicConfig(level=logging.INFO)
handler = logging.StreamHandler()
app.logger.addHandler(handler)

# set up storage/db stuff
credentials = service_account.Credentials.from_service_account_file("serviceKey.json")
db = firestore.Client(credentials=credentials, project="podify-1b981")
storage_client = storage.Client(credentials=credentials, project="podify-1b981")
podcast_bucket = "podify-1b981.appspot.com"

# Embedding model for Pinecone
# EMBEDDING_MODEL = SentenceTransformer("all-mpnet-base-v2")


@app.route("/")
def hello_world():
    target = os.environ.get("TARGET", "World")
    return "Hello {}!\n".format(target)

@app.route("/get_cards", methods=["POST"])
def get_cards():
    # Given a user's list of preferences, get all cards. Will get related cards too
    preferences: List[str] = request.json.get("preferences")
    try:
        cards_ref = db.collection("GLOBAL_CARDS")
        query = cards_ref.where("preference", "in", preferences)
        results = query.get()
        return_vals = []
        for card in results:
            return_vals.append(card.to_dict())
        return jsonify({"cards": return_vals}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

  
@app.route("/generate_cards", methods=["POST"])
def generate_cards():
    preferences = get_prefs()
    date = current_date()
    failures = []
    try:
        for pref in preferences:
            success = card_pref(pref, date)
            if not success:
                failures.append(pref)
        return jsonify({"status" : "success", "failures" : ", ".join(failures)}), 200
    except Exception as e:
        return jsonify({"message": str(e), }), 400

@app.route("/card_more_info", methods=["POST"])
def card_more_info():
    card_id = request.json.get("card_id")
    question = request.json.get("question")
    pref = request.json.get("preference")
    card = request.json.get("card")
    date = firebase_format_date(request.json.get("date"))

    pref_ref = db.collection("GLOBAL_PREFS").document(pref)
    try:
        doc = pref_ref.get()
        if doc.exists:
            research = doc.to_dict()
            sources = research[date]
            answer = answer_question(sources, card, question)
            return jsonify({"answer": answer}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400 

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))