import streamlit as st
import requests
    

st.set_page_config(page_title="HistoryAI", page_icon="📜")

st.title("📜 HistoryAI")

# 📌 Initialiser l'historique des messages s'il n'existe pas encore
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# st.markdown("🔍 **Rechercher dans la conversation**")
# search_query = st.text_input("Entrez un mot-clé pour filtrer la conversation ")

# if search_query:
#     filtered_messages = [msg for msg in st.session_state["messages"] if search_query.lower() in msg[1].lower()]
#     if filtered_messages:
#         st.markdown("### 📌 Résultats de la recherche")
#         for role, text in filtered_messages:
#             with st.chat_message(role):
#                 st.markdown(text)
#     else:
#         st.warning("Aucun message ne correspond à votre recherche.")

# 📌 Affichage des messages sous forme de chat
for message in st.session_state["messages"]:
    role, text = message
    with st.chat_message(role):
        st.markdown(text)

# 📌 Ajouter une zone de saisie plus large pour écrire plus de texte
user_input = st.text_area("Posez votre question historique 👇", height=100)

# 📌 Organisation des boutons dans deux colonnes
col1, col2 = st.columns([1, 3])

with col1:
    clear_button = st.button("🔄 Réinitialiser", use_container_width=True)

with col2:
    send_button = st.button("📩 Envoyer", use_container_width=True)


# 📌 Réinitialiser l'historique du chat si l'utilisateur appuie sur le bouton
if clear_button:
    st.session_state["messages"] = []
    st.rerun()

# 📌 Envoyer la requête lorsque l'utilisateur clique sur "Envoyer"
if send_button and user_input:
    # 📌 Afficher immédiatement la question de l'utilisateur
    with st.chat_message("user"):
        st.markdown(user_input)

    # 📌 Indicateur de chargement pendant que le bot répond
    with st.spinner("💬 Le chatbot réfléchit..."):
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"user_id": "123", "message": user_input}
        )

    # 📌 Vérifier si la réponse contient bien "response"
    if response.status_code == 200:
        response_json = response.json()
        response_text = response_json.get("response", "⚠️ Réponse inattendue.")
    else:
        response_text = f"⚠️ Erreur {response.status_code}: Impossible de contacter le chatbot."

    # 📌 Afficher la réponse du bot sous forme de bulle
    with st.chat_message("assistant"):
        st.markdown(response_text)

    # 📌 Ajouter la conversation à l'historique
    st.session_state["messages"].append(("user", user_input))
    st.session_state["messages"].append(("assistant", response_text))

    # 📌 Rafraîchir l'affichage après envoi
    st.rerun()