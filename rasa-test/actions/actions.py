import faiss
import pandas as pd
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import ollama

# 🔥 Charger le modèle NLP
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

# 🔹 Charger FAISS et les données
index = faiss.read_index("data/events_faiss.index")
df_events = pd.read_pickle("data/events_mapping.pkl")

# 🔹 Charger TF-IDF
vectorizer = pickle.load(open("data/tfidf_vectorizer.pkl", "rb"))
tfidf_matrix = pickle.load(open("data/tfidf_matrix.pkl", "rb"))

# class ActionRechercheEvenement(Action):
#     def name(self) -> Text:
#         return "action_recherche_evenement"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         user_input = tracker.latest_message.get("text")

#         if not user_input:
#             dispatcher.utter_message(text="Je n'ai pas compris votre demande.")
#             return []

#         # 🔹 Recherche avec FAISS
#         query_embedding = model.encode([user_input])
#         D, I = index.search(np.array(query_embedding), k=1)
#         best_match_id = I[0][0]
#         confidence = D[0][0]

#         # 🔹 Vérifier le seuil de confiance FAISS (si > 0.5, on évite de répondre)
#         if confidence > 0.5:
#             # 🔹 Fallback avec TF-IDF
#             query_tfidf = vectorizer.transform([user_input])
#             cosine_similarities = cosine_similarity(query_tfidf, tfidf_matrix).flatten()
#             best_match_id = cosine_similarities.argmax()

#         # 🔹 Récupérer l'événement trouvé
#         event = df_events[df_events["ID"] == best_match_id].iloc[0]
#         response = f"📜 **{event['Nom']}**\n📅 **Date** : {event['Date']}\n📍 **Lieu** : {event['Lieu']}\n📝 **Résumé** : {event['Résumé']}\n🔎 **Plus d'infos** : {event['URL']}"

#         dispatcher.utter_message(text=response)
#         return []
    

class ActionRechercheEvenementDeepSeek(Action):
    def name(self):
        return "action_recherche_evenement_deepseek"

    def run(self, dispatcher, tracker, domain):
        user_input = tracker.latest_message.get("text")

        if not user_input:
            dispatcher.utter_message(text="Je n'ai pas compris ta question.")
            return []

        # 🔹 Envoyer la requête à DeepSeek R1 via Ollama
        response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": f"Réponds comme un historien : {user_input}"}])

        deepseek_response = response["message"]["content"]
        dispatcher.utter_message(text=deepseek_response)

        return []
    
class ActionGenerationQuizzDeepSeek(Action):
    def name(self):
        return "action_generation_quizz_deepseek"

    def run(self, dispatcher, tracker, domain):
        user_input = tracker.latest_message.get("text")

        # 🔹 Générer un quizz historique avec DeepSeek R1
        response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": f"Crée un quizz de 5 questions à choix multiple sur {user_input}. Ne donne pas les réponses."}])
        print(response)
        quizz_response = response["message"]["content"]
        dispatcher.utter_message(text=quizz_response)

        return []
    
class ActionFicheRevisionDeepSeek(Action):
    def name(self):
        return "action_fiche_revision_deepseek"

    def run(self, dispatcher, tracker, domain):
        user_input = tracker.latest_message.get("text")

        # 🔹 Générer une fiche de révision
        response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": f"Rédige une fiche de révision détaillée sur {user_input}, comprenant :\n1. Un résumé\n2. Les causes\n3. Les conséquences\n4. Les chiffres clés."}])

        fiche_response = response["message"]["content"]
        dispatcher.utter_message(text=fiche_response)

        return []
    
class ActionComparaisonGuerresDeepSeek(Action):
    def name(self):
        return "action_comparaison_guerres_deepseek"

    def run(self, dispatcher, tracker, domain):
        user_input = tracker.latest_message.get("text")

        # 🔹 Comparer deux guerres
        response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": f"Compare ces deux guerres : {user_input}. Indique les points communs et les différences."}])

        comparaison_response = response["message"]["content"]
        dispatcher.utter_message(text=comparaison_response)

        return []