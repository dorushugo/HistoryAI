import faiss
import pandas as pd
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# 🔥 Charger le modèle NLP
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

# 🔹 Charger FAISS et les données
index = faiss.read_index("data/events_faiss.index")
df_events = pd.read_pickle("data/events_mapping.pkl")

# 🔹 Charger TF-IDF
vectorizer = pickle.load(open("data/tfidf_vectorizer.pkl", "rb"))
tfidf_matrix = pickle.load(open("data/tfidf_matrix.pkl", "rb"))

class ActionRechercheEvenement(Action):
    def name(self) -> Text:
        return "action_recherche_evenement"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_input = tracker.latest_message.get("text")

        if not user_input:
            dispatcher.utter_message(text="Je n'ai pas compris votre demande.")
            return []

        # 🔹 Recherche avec FAISS
        query_embedding = model.encode([user_input])
        D, I = index.search(np.array(query_embedding), k=1)
        best_match_id = I[0][0]
        confidence = D[0][0]

        # 🔹 Vérifier le seuil de confiance FAISS (si > 0.5, on évite de répondre)
        if confidence > 0.5:
            # 🔹 Fallback avec TF-IDF
            query_tfidf = vectorizer.transform([user_input])
            cosine_similarities = cosine_similarity(query_tfidf, tfidf_matrix).flatten()
            best_match_id = cosine_similarities.argmax()

        # 🔹 Récupérer l'événement trouvé
        event = df_events[df_events["ID"] == best_match_id].iloc[0]
        response = f"📜 **{event['Nom']}**\n📅 **Date** : {event['Date']}\n📍 **Lieu** : {event['Lieu']}\n📝 **Résumé** : {event['Résumé']}\n🔎 **Plus d'infos** : {event['URL']}"

        dispatcher.utter_message(text=response)
        return []