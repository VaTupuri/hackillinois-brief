from datetime import datetime
from gcloud_helper import *
from config import GPT_API_KEYS, OCTO_KEYS
from llm_functions import *
from search import search

def search_one(user):
    user_prefs = get_firebase_data(user, "Preferences", "prefs")
    if not user_prefs:
        return
    current_date = datetime.now().strftime("%Y%m%d")
    for pref in user_prefs:
        pref = pref.lower()
        field_key = f"research-{current_date}"
        has_searched = get_firebase_data("GLOBAL_PREFS", pref, field_key)
        if has_searched == None:
            urls, context = search(pref + " articles", user) 
            add_info(user, urls, "urls")
            if not context:
                print(f"NO NEWS ON {pref} on {current_date}")
            add_firebase_data("GLOBAL_PREFS", pref, field_key, context)
            print("ADDED RESEARCH FOR: ", pref)
        else:
            print(f"No need to search for topic {pref}")

#TODO PARALLELIZE
def batch_search_all_prefs():
    users = get_all_users()
    for user in users:
        user_prefs = get_firebase_data(user, "Preferences", "prefs")
        if not user_prefs:
            continue
        current_date = datetime.now().strftime("%Y%m%d")
        for pref in user_prefs:
            pref = pref.lower()
            field_key = f"research-{current_date}"
            has_searched = get_firebase_data("GLOBAL_PREFS", pref, field_key)
            if has_searched == None:
                urls, context = search(pref + " recent news", None) 
                add_info(user, urls, "urls")
                if not context:
                    print(f"NO NEWS ON {pref} on {current_date}")
                add_firebase_data("GLOBAL_PREFS", pref, field_key, context)
                print("ADDED RESEARCH FOR: ", pref)
            else:
                print(f"No need to search for topic {pref}")

        
# def batch_card_all_prefs():
#     current_date = datetime.now().strftime("%Y%m%d")
#     credentials = service_account.Credentials.from_service_account_file(
#         "serviceKey.json"
#     )
#     db = firestore.Client(credentials=credentials, project="podify-1b981")
#     global_prefs = db.collection("GLOBAL_PREFS")
#     docs = global_prefs.get()
#     i = 0
#     for pref in docs: 
#         if i > 4:
#             break
#         card_pref(pref.id, current_date)
#         i+=1

def card_pref(pref, current_date):
    try:
        print("WRITING CARD FOR: ", pref)
        key = f"research-{current_date}" #TODO: change
        research = get_firebase_data("GLOBAL_PREFS", pref, key)
        
        query = f"Take the content from the source below and summarize it with bullet points denoted by '*'. Seperate different key points by a new line." 
            
        for source in research:
            title, info = source.split("INFORMATION")
            if "SOURCE" in title:
                title_text = title.split("SOURCE ")[1]
            else:
                title_text = title
            inp = query + source
            text = mixtralGenerateText(inp, 400)
            print(text)
            card_id = add_card(title_text, current_date, text, pref)
        return True
    except Exception as e:
        print(e)
        return False

if __name__ == "__main__":
    card_pref("ai", current_date=datetime.now().strftime("%Y%m%d"))