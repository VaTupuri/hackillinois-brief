from google.cloud import firestore, storage
from google.oauth2 import service_account
from datetime import datetime, timedelta
from google.cloud import tasks_v2
import firebase_admin
from firebase_admin import messaging
from firebase_admin import credentials
#import datetime
import json


def get_yesterdays_urls(user_id):
    credentials = service_account.Credentials.from_service_account_file(
        "serviceKey.json"
    )
    db = firestore.Client(credentials=credentials, project="podify-1b981")
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    users_collection = db.collection(user_id)
    user_doc_ref = users_collection.document("URLs_Used")
    summary_doc = user_doc_ref.get()
    if summary_doc.exists:
        summary_key = f"url-{user_id}-{yesterday_date}.mp3"
        summary_data = summary_doc.to_dict()
        # print(summary_data.keys(), summary_key in summary_data, summary_key)

        if summary_key in summary_data:
            return summary_data[summary_key]
        else:
            print(f"No Podcast Yesterday so we dont have URLs for {user_id}")

    return ""


def add_info(user_id, info, type, file_name=None):
    credentials = service_account.Credentials.from_service_account_file(
        "serviceKey.json"
    )
    db = firestore.Client(credentials=credentials, project="podify-1b981")
    # Specify the collection and document for users
    users_collection = db.collection(user_id)
    if not file_name:
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"{user_id}-{current_date}.mp3"
    else:
        filename = file_name

    if type == "script":
        user_doc_ref = users_collection.document("Scripts")

        # Create a new document with script and urls fields

        new_script_data = {f"script-{filename}": info}

        # Set the document with the specified data
        user_doc_ref.set(new_script_data, merge=True)
    else:
        user_doc_ref = users_collection.document("URLs_Used")

        new_url_data = {f"url-{filename}": info}

        # Set the document with the specified data
        user_doc_ref.set(new_url_data, merge=True)
    # print("add info complete")


def add_pref_queries(preference, query_list):
    credentials = service_account.Credentials.from_service_account_file(
        "serviceKey.json"
    )
    db = firestore.Client(credentials=credentials, project="podify-1b981")
    # Specify the collection and document for users
    users_collection = db.collection("GLOBAL_PREFS")
    user_doc_ref = users_collection.document(preference)
    # for query in query_list:
    new_script_data = {"Queries": query_list}
    user_doc_ref.set(new_script_data, merge=True)


def extract_questions(query_string):
    lines = query_string.split("\n")
    questions = []
    # print(lines)
    for line in lines:
        question = line[3:]
        questions.append(question)

    # print(questions)
    return questions


def add_research(topic, data):
    credentials = service_account.Credentials.from_service_account_file(
        "serviceKey.json"
    )
    db = firestore.Client(credentials=credentials, project="podify-1b981")
    # Specify the collection and document for users
    users_collection = db.collection("GLOBAL_PREFS")
    user_doc_ref = users_collection.document(topic)
    new_script_data = {"Data": data}
    user_doc_ref.set(new_script_data, merge=True)

def get_prefs():
    credentials = service_account.Credentials.from_service_account_file(
        "serviceKey.json"
    )
    db = firestore.Client(credentials=credentials, project="podify-1b981")
    # Specify the collection and document for users
    collection_name = "GLOBAL_PREFS"
    collection_ref = db.collection(collection_name)

    # Get all documents in the collection
    documents = collection_ref.get()

    # Iterate over documents
    prefs = []
    for doc in documents:
        prefs.append(doc.id)

    return prefs


def get_firebase_data(collection, document, field):
    credentials = service_account.Credentials.from_service_account_file(
        "serviceKey.json"
    )
    db = firestore.Client(credentials=credentials, project="podify-1b981")
    # Specify the collection and document for users
    users_collection = db.collection(collection)
    user_doc_ref = users_collection.document(document)
    # for query in query_list:
    doc_data = user_doc_ref.get().to_dict()

    # Check if the document exists and has the "Queries" field
    if doc_data and field in doc_data:
        # Print each query in the "Queries" field
        return doc_data[field]
        # print(query)
    else:
        # print("No data found for topic:", document)
        return None

def get_device_tokens(user_id):
    credentials = service_account.Credentials.from_service_account_file(
        "serviceKey.json"
    )
    db = firestore.Client(credentials=credentials, project="podify-1b981")
    # Specify the collection and document for users
    users_collection = db.collection(user_id)
    user_doc_ref = users_collection.document('Devices')
    if user_doc_ref.get().to_dict():
        return user_doc_ref.get().to_dict()
    else:
        return None
    
def notify_device(registration_token, title, body):
    # See documentation on defining a message payload.
    if not firebase_admin._apps:
    # Firebase app has not been initialized yet
        cred = credentials.Certificate('serviceKey.json')
        firebase_admin.initialize_app(cred)
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=registration_token,
    )
    # Send a message to the device corresponding to the provided
    # registration token.
    try:
        response = messaging.send(message)
        print('Successfully sent message:', response)
    except:
        print("unsuccessful for " + registration_token)
    # Response is a message ID string.
    

def notify_user(user_email, title, body):
    device_tokens = get_device_tokens(user_email)
    if device_tokens:
        print(device_tokens.keys())
        for token in device_tokens.keys():
            print("sending notif")
            notify_device(token, title, body)
    else:
        print("Device token not found for email:", user_email)

def get_all_users():
    credentials = service_account.Credentials.from_service_account_file(
        "serviceKey.json"
    )
    db = firestore.Client(credentials=credentials, project="podify-1b981")
    collections = db.collections()

    return [collection.id for collection in collections if '@' in collection.id]

def add_card(title, date, text, preference):
    credentials = service_account.Credentials.from_service_account_file(
        "serviceKey.json"
    )
    db = firestore.Client(credentials=credentials, project="podify-1b981")
    cards_ref = db.collection("GLOBAL_CARDS")

    card_data = {
        "title": title,
        "date": date,
        "text": text,
        "preference": preference
    }

    try:
        # Add a new document
        new_card_ref = cards_ref.add(card_data)
        # new_card_ref is a tuple of (DocumentReference, datetime with the creation time)
        # You can get the document ID from the DocumentReference
        print(f"Card added with ID: {new_card_ref[0]}")
        return new_card_ref[0]  # Return the new document ID
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def add_firebase_data(collection, document, field, data):
    credentials = service_account.Credentials.from_service_account_file(
        "serviceKey.json"
    )
    db = firestore.Client(credentials=credentials, project="podify-1b981")
    # Specify the collection and document for users

    users_collection = db.collection(collection)
    user_doc_ref = users_collection.document(document)
    new_script_data = {field: data}
    user_doc_ref.set(new_script_data, merge=True)
    # except Exception e:
    #     print(e)
    #     print(f"UPLOAD FAILED FOR {collection},{document}, {field}")

def get_firebase_data(collection, document, field):
    credentials = service_account.Credentials.from_service_account_file(
        "serviceKey.json"
    )
    db = firestore.Client(credentials=credentials, project="podify-1b981")
    # Specify the collection and document for users
    users_collection = db.collection(collection)
    user_doc_ref = users_collection.document(document)
    # for query in query_list:
    doc_data = user_doc_ref.get().to_dict()

    # Check if the document exists and has the "Queries" field
    if doc_data and field in doc_data:
        # Print each query in the "Queries" field
        return doc_data[field]
        # print(query)
    else:
        # print("No data found for topic:", document)
        return None
    
def get_docs_from_collection(collection):
    credentials = service_account.Credentials.from_service_account_file(
        "serviceKey.json"
    )
    db = firestore.Client(credentials=credentials, project="podify-1b981")
    # Specify the collection and document for users
    collection_ref = db.collection(collection)
    # Get all documents in the collection
    documents = collection_ref.list_documents()
    # Extract document IDs
    document_ids = [doc.id for doc in documents]
    return document_ids