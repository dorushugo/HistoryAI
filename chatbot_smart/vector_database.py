import os
import faiss
import pandas as pd
import re
import spacy
import unicodedata
import numpy as np
from sentence_transformers import SentenceTransformer

# 🔥 Chargement du modèle NLP français pour la lemmatisation
nlp = spacy.load("fr_core_news_lg") # modèle sm plus petit si besoin

# 🔹 Charger les données
df = pd.read_csv("guerres_details_full_clean.csv")

df.fillna("", inplace=True)
# 🔹 Nettoyage des textes
def clean_text(text):
    if pd.isna(text):
        return ""

    # Convertir en minuscules
    text = text.lower()

     # Supprimer les accents
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    
   # Remplacer les caractères spéciaux sauf les nombres et les années
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", text)
    
    # Supprimer les espaces en trop
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

# 🔹 Générer le texte structuré pour chaque guerre
df["Texte_Indexé"] = df.apply(lambda row: f"""
🏛️ Nom : {row['Nom']}
📅 Date : {row['Date']}
📍 Lieu : {row['Lieu']}
⚔️ Issue : {row['Issue']}
📜 Résumé : {row['Résumé']}
🔎 Sections : {row['Sections']}
📖 Extrait : {row['Contenu_complet'][:500]}...
""", axis=1)

# df["Texte_Indexé"] = df["Texte_Indexé"].apply(clean_text)

# 🔹 Stopwords et Lemmatisation
stopwords_fr = set(nlp.Defaults.stop_words)

def preprocess_text(text):
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if token.text not in stopwords_fr and not token.is_punct]
    return " ".join(tokens)

# df["Texte_Indexé"] = df["Texte_Indexé"].apply(preprocess_text)

# 🔹 Vérifier le contenu final
# print(df[["Texte_Indexé"]].head())

# # 🔹 Initialiser le modèle d'embedding en français
# model = SentenceTransformer("dangvantuan/sentence-camembert-base")
# model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
model = SentenceTransformer('Lajavaness/bilingual-document-embedding', trust_remote_code=True)

# 🔹 Générer les embeddings
descriptions = df["Texte_Indexé"].tolist()
embeddings = model.encode(descriptions)
print(f"✅ Dimension des embeddings FAISS : {embeddings.shape[1]}")


# 🔹 Créer l'index FAISS
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# 🔹 Sauvegarder l'index FAISS
if not os.path.exists("data"):
    os.makedirs("data")

faiss.write_index(index, "data/guerres_faiss_NLP2.index")
# 🔹 Sauvegarder le mapping des guerres
df["ID"] = range(len(df))
df_mapping = df[["ID", "Nom", "Date", "Lieu", "Issue", "Résumé", "Conclusion", "Sections", "URL"]]
df_mapping.to_pickle("data/guerres_mapping_NLP.pkl")

print("✅ Base vectorielle mise à jour avec succès !")