from fastapi import FastAPI
from pydantic import BaseModel
import ollama
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import joblib

# 🔹 Charger le modèle et le vectorizer entraînés
vectorizer = joblib.load("vectorizer.pkl")
classifier = joblib.load("intent_classifier.pkl")

def detect_intent(message):
    """ Détecte l’intention de l’utilisateur """
    X = vectorizer.transform([message])
    print(classifier.predict(X)[0])
    return classifier.predict(X)[0]
    
app = FastAPI()

# 📌 Définir le modèle Pydantic pour la requête
class ChatRequest(BaseModel):
    user_id: str
    message: str

# 🔹 Charger FAISS et le modèle d'embeddings
index = faiss.read_index("data/guerres_faiss.index")
df_events = pd.read_pickle("data/guerres_mapping.pkl")
embedding_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

quiz_sessions = {}
conversation_memory = {}

def generate_quiz(topic):
    """ Génère un quizz à partir de la base de données vectorielle ou indique que le sujet est inconnu """
    global quiz_sessions
    global conversation_memory
    user_id ="123"

        # ✅ Créer un texte avec les derniers messages
    conversation_history = conversation_memory[user_id]
    
    # ✅ Vérifier que chaque élément est bien un dictionnaire
    if not all(isinstance(msg, dict) for msg in conversation_history):
        print("⚠️ Erreur : `conversation_memory` contient des données incorrectes ! Réinitialisation...")
        conversation_memory[user_id] = []
        conversation_history = []

    # 🔹 Construire la conversation sous forme de texte
    conversation_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation_history])
    print(conversation_text)

    # 🔎 1️⃣ Recherche du sujet dans la base vectorielle FAISS
    query_embedding = embedding_model.encode([topic])
    D, I = index.search(np.array(query_embedding), k=1)  # Récupérer le meilleur résultat
    best_match_id = I[0][0]
    confidence = D[0][0]

    SEUIL_CONFIANCE_BAS = 10  # En dessous, on dit qu'on ne connaît pas
    SEUIL_CONFIANCE_LLM = 5  # Entre 5 et 10, on peut utiliser le LLM pour compléter

    if confidence < SEUIL_CONFIANCE_LLM:
        # 📌 Récupérer les informations du sujet
        event = df_events.iloc[best_match_id]
        contexte = (
            f"📜 **{event['Nom']}**\n"
            f"📅 **Date** : {event['Date']}\n"
            f"📍 **Lieu** : {event['Lieu']}\n"
            f"📝 **Résumé** : {event['Résumé']}\n"
        )
        print(conversation_memory)
        # 🎯 2️⃣ Générer un quizz basé sur ces informations
        llm_prompt = f"""
        Voici l'historique de la conversation avec l'utilisateur :
        {conversation_text}
        
        Mets-toi dans la peau d'un assistant pour les révisions.
        Utilise les informations suivantes pour créer un quizz sur {topic}.
        Donne 5 questions à choix multiples pertinentes sans donner les réponses.

        **Informations :**
        {contexte}
        """

        response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": llm_prompt}])
        llm_quiz = response["message"]["content"]

        # 📌 Sauvegarde des questions générées
        quiz_sessions[user_id] = [(q.strip(), "??") for q in llm_quiz.split("\n") if q.strip()]

        return f"📋 Quizz généré avec les données disponibles :\n\n{llm_quiz}"

    elif confidence > SEUIL_CONFIANCE_LLM and confidence < SEUIL_CONFIANCE_BAS:
        # 📌 3️⃣ Confiance trop faible → On utilise le LLM sans source vérifiée
        llm_prompt = f"""
        Mets-toi dans la peau d'un assistant pour les révisions.
        Génère un quizz sur {topic}.
        Donne 5 questions à choix multiples pertinentes sans donner les réponses.
        """

        response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": llm_prompt}])
        llm_quiz = response["message"]["content"]

        # 📌 Sauvegarde temporaire des questions générées (sans réponses)
        quiz_sessions[user_id] = [(q.strip(), "??") for q in llm_quiz.split("\n") if q.strip()]

        return f"📋 Quizz généré par l'IA (données incertaines) :\n\n{llm_quiz}"

    else:
        # 📌 4️⃣ Confiance trop basse → On refuse de répondre
        return "⚠️ Désolé, je n’ai pas assez d’informations pour générer un quizz sur ce sujet."

def provide_quiz_answers(user_id):
    """ Renvoie les réponses du dernier quizz demandé par l'utilisateur, si disponible """

    global quiz_sessions  # 📌 Permet d'accéder à la variable globale
    global conversation_memory
        # ✅ Créer un texte avec les derniers messages
    conversation_history = conversation_memory[user_id]
    
    # ✅ Vérifier que chaque élément est bien un dictionnaire
    if not all(isinstance(msg, dict) for msg in conversation_history):
        print("⚠️ Erreur : `conversation_memory` contient des données incorrectes ! Réinitialisation...")
        conversation_memory[user_id] = []
        conversation_history = []

    # 🔹 Construire la conversation sous forme de texte
    conversation_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation_history])
    print(conversation_text)

    if user_id not in quiz_sessions:
        return "⚠️ Aucun quizz en cours. Demandez-moi d’en générer un !"

    # 📌 Récupérer les questions stockées
    questions = quiz_sessions[user_id]

    # 🎯 Vérifier si on a déjà les réponses
    if "??" not in [answer for _, answer in questions]:
        return "\n".join([f"✅ {q} : **{a}**" for q, a in questions])

    # 🎯 Si les réponses sont inconnues, demander au LLM
    print("⚠️ Réponses manquantes, génération par LLM...")

    llm_prompt = f"""
    Voici l'historique de la conversation avec l'utilisateur :
    {conversation_text}

    Voici un quizz d'histoire :
    {chr(10).join([q for q, _ in questions])}

    Donne une réponse précise pour chaque question sous forme de liste numérotée.
    """

    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": llm_prompt}])
    llm_answers = response["message"]["content"].split("\n")

    # 📌 Mettre à jour les réponses dans la session
    for i, (q, _) in enumerate(questions):
        if i < len(llm_answers):
            quiz_sessions[user_id][i] = (q, llm_answers[i].strip())

    return f"📋 Réponses du quizz :\n\n{chr(10).join(llm_answers)}"

def generate_summary(topic):
    """ Génère un résumé simple et pédagogique pour aider un élève à réviser """
    global conversation_memory
    user_id ="123"

    # ✅ Créer un texte avec les derniers messages
    conversation_history = conversation_memory[user_id]
    
    # ✅ Vérifier que chaque élément est bien un dictionnaire
    if not all(isinstance(msg, dict) for msg in conversation_history):
        print("⚠️ Erreur : `conversation_memory` contient des données incorrectes ! Réinitialisation...")
        conversation_memory[user_id] = []
        conversation_history = []

    # 🔹 Construire la conversation sous forme de texte
    conversation_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation_history])
    print(conversation_text)
    # 🔎 1️⃣ Recherche de l'événement dans FAISS
    query_embedding = embedding_model.encode([topic])
    D, I = index.search(np.array(query_embedding), k=1)
    best_match_id = I[0][0]
    confidence = D[0][0]

    SEUIL_CONFIANCE_BAS = 10

    if confidence > SEUIL_CONFIANCE_BAS:
        event = df_events.iloc[best_match_id]
        contexte = f"📜 **{event['Nom']}**\n📅 **Date** : {event['Date']}\n📍 **Lieu** : {event['Lieu']}\n📝 **Résumé** : {event['Résumé']}"

        # 🎯 Demander au LLM un résumé pour un élève
        llm_prompt = f"""
        Voici l'historique de la conversation avec l'utilisateur :
        {conversation_text}

        Tu es un professeur d'histoire. Rédige un résumé pédagogique sur {event['Nom']} destiné à un élève de lycée.
        Utilise ces informations :
        {contexte}

        Explique de manière simple et claire, en 150 mots maximum.
        """

        response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": llm_prompt}])

        return f"📜 **Résumé pédagogique de {event['Nom']}** :\n\n{response['message']['content']}"

    return "⚠️ Désolé, je n’ai pas assez d’informations pour générer un résumé sur ce sujet."

def search_history(message):
    """ Recherche un événement historique et l'explique en détail pour un élève """
    global conversation_memory
    user_id ="123"

    # ✅ Créer un texte avec les derniers messages
    conversation_history = conversation_memory[user_id]
    
    # ✅ Vérifier que chaque élément est bien un dictionnaire
    if not all(isinstance(msg, dict) for msg in conversation_history):
        print("⚠️ Erreur : `conversation_memory` contient des données incorrectes ! Réinitialisation...")
        conversation_memory[user_id] = []
        conversation_history = []

    # 🔹 Construire la conversation sous forme de texte
    conversation_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation_history])
    print(conversation_text)

    # 🔎 Générer l'embedding de la requête
    query_embedding = embedding_model.encode([message])
    D, I = index.search(np.array(query_embedding), k=1)
    best_match_id = I[0][0]
    confidence = D[0][0]

    SEUIL_CONFIANCE_BAS = 10

    if confidence > SEUIL_CONFIANCE_BAS:
        return "⚠️ Désolé, je n’ai pas trouvé d’informations précises sur ce sujet."

    event = df_events.iloc[best_match_id]
    contexte = f"📜 **{event['Nom']}**\n📅 **Date** : {event['Date']}\n📍 **Lieu** : {event['Lieu']}\n📝 **Résumé** : {event['Résumé']}"

    # 🎯 Demander au LLM d'expliquer le sujet en détail
    llm_prompt = f"""
    Voici l'historique de la conversation avec l'utilisateur :
    {conversation_text}

    Explique à un élève de lycée l'événement historique suivant :
    {contexte}

    Rédige une explication détaillée et pédagogique en 300 mots maximum.
    Structure la réponse en introduction, développement et conclusion.
    """

    response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": llm_prompt}])

    return f"📜 **Explication détaillée de {event['Nom']}** :\n\n{response['message']['content']}"

@app.post("/chat")
def chat(request: ChatRequest):
    """ Gère la conversation et détecte l’intention automatiquement """

    user_id = request.user_id
    message = request.message.lower()

    # 🎯 1️⃣ Vérifier que l'utilisateur a une liste d'historique
    if user_id not in conversation_memory:
        conversation_memory[user_id] = []  # 📌 Créer une liste vide pour ce user
    conversation_history = conversation_memory[user_id]


    # 🎯 1️⃣ Détecter l’intention de la requête
    intent = detect_intent(message)

    print(f"📩 Message reçu : {message} → Intention détectée : {intent}")

    # 🎯 2️⃣ Rediriger vers la bonne fonction
    if intent == "quizz":
        response_text = generate_quiz(message)
    elif intent == "quizz_reponses":
        response_text = provide_quiz_answers(user_id)
    elif intent == "résumé":
        response_text = generate_summary(message)
    elif intent == "recherche":
        response_text = search_history(message)
    else:
        response_text = "⚠️ Je ne suis pas sûr de comprendre. Peux-tu reformuler ?"
    # 📌 Stocker la réponse dans la mémoire
    conversation_history.append({"role": "assistant", "content": response_text})
    return {"response": response_text}

# @app.post("/chat")
# def chat(request: ChatRequest):
#     """ Gère la conversation avec mémoire contextuelle """

#     user_id = request.user_id
#     message = request.message

#     # 📌 Vérifier que le message n'est pas vide
#     if not message.strip():
#         return {"response": "⚠️ Je n'ai pas compris votre message."}

#     print(f"📩 Message reçu de {user_id}: {message}")

#     try:
#         query_embedding = embedding_model.encode([message])
#         D, I = index.search(np.array(query_embedding), k=1)
#         best_match_id = I[0][0]
#         confidence = D[0][0]
#         print(f"Confidence {confidence}")

#         if confidence < 0.5:
#             event = df_events.iloc[best_match_id]
#             response_text = f"📜 **{event['Nom']}**\n📅 **Date** : {event['Date']}\n📍 **Lieu** : {event['Lieu']}\n📝 **Résumé** : {event['Résumé']}\n🔎 **Plus d'infos** : {event['URL']}"
#             print(response_text)
#         else:
#             response_text = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": message}])["message"]["content"]
#             print(response_text)

#     except Exception as e:
#         print(f"⚠️ Erreur: {e}")
#         response_text = "⚠️ Désolé, une erreur est survenue."

#     return {"response": response_text}




# import numpy as np
# import pandas as pd

# # 🔹 Liste de requêtes historiques
# test_messages = [
#     "Guerre de la Ligue de Cambrai", "Guerre de Trente Ans", "Guerre de Dévolution",
#     "Guerre de Hollande", "Guerre de la Ligue d'Augsbourg", "Guerre de Succession d'Espagne",
#     "Guerre de la Quadruple-Alliance", "Guerre de Succession de Pologne", "Guerre de Succession d'Autriche",
#     "Guerre de Sept Ans", "Guerre d'Indépendance des États-Unis", "Guerres de la Révolution française",
#     "Guerres napoléoniennes", "Guerre de 1812", "Guerre d'indépendance grecque",
#     "Guerre de Crimée", "Guerre de Sécession", "Guerre franco-prussienne",
#     "Guerre des Boers", "Première Guerre mondiale", "Guerre civile russe",
#     "Guerre d'indépendance irlandaise", "Guerre civile chinoise", "Guerre d'Espagne",
#     "Seconde Guerre mondiale", "Guerre de Corée", "Guerre d'Algérie",
#     "Guerre du Vietnam", "Guerre du Yom Kippour", "Guerre d'Afghanistan",
#     "Guerre Iran-Irak", "Guerre du Golfe", "Guerre de Bosnie",
#     "Guerre du Kosovo", "Guerre d'Irak", "Guerre civile syrienne",
#     "Guerre du Donbass", "Guerre du Haut-Karabagh", "Guerre civile libyenne",
#     "Guerre civile yéménite", "Guerre du Mali", "Guerre civile centrafricaine",
#     "Guerre du Darfour", "Guerre civile sud-soudanaise", "Guerre du Tigré",
#     "Guerre civile éthiopienne", "Guerre civile angolaise", "Guerre civile mozambicaine",
#     "Guerre civile sierra-léonaise", "Guerre civile libérienne"
# ]

# # 🔹 Stocker les résultats
# test_results = []

# for message in test_messages:
#     query_embedding = embedding_model.encode([message])
#     D, I = index.search(np.array(query_embedding), k=1)
#     best_match_id = I[0][0]
#     confidence = D[0][0]
    
#     best_match = df_events.iloc[best_match_id]["Nom"] if best_match_id < len(df_events) else "Aucun résultat"

#     test_results.append({
#         "Message": message,
#         "Meilleur résultat": best_match,
#         "Score de confiance": confidence
#     })

# # 🔹 Convertir en DataFrame et afficher les résultats
# df_test_results = pd.DataFrame(test_results)
# print(df_test_results)

# # 🔹 Sauvegarder dans un fichier CSV pour analyse
# df_test_results.to_csv("faiss_test_results2.csv", index=False)