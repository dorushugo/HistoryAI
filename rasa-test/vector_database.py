import os
import faiss
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle

# 🔥 Modèle d'embeddings en français
# model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

# 🔹 Charger les données à partir d'un DataFrame pandas (ex: récupéré d'un CSV)
df = pd.read_csv("guerres_details_completes.csv")

# #AMELIORATION 
# # 🔹 Générer des descriptions enrichies (Nom + Date + Résumé)
# df["Texte_Indexé"] = df["Nom"] + " " + df["Date"] + " " + df["Résumé"]

# 🔹 Vérifier que les colonnes attendues existent
colonnes_attendues = ["Nom", "URL", "Date", "Lieu", "Issue", "Résumé", "Conclusion", "Sections"]
for col in colonnes_attendues:
    if col not in df.columns:
        raise ValueError(f"⚠️ La colonne '{col}' est absente du DataFrame ! Vérifie tes données.")


# 🔹 Remplir les valeurs manquantes pour éviter les erreurs
df.fillna("", inplace=True)

df["Texte_Indexé"] = (
    df["Nom"] + " " + df["Date"] + " " + df["Lieu"] + " " +
    df["Résumé"] + " " + df["Conclusion"]
)

# 🔹 Générer des embeddings pour la colonne `Texte_Indexé`
descriptions = df["Texte_Indexé"].tolist()
embeddings = model.encode(descriptions)

# 🔹 Générer des embeddings pour ce texte enrichi
# descriptions = df["Texte_Indexé"].tolist()
# embeddings = model.encode(descriptions)

# 🔹 Créer l'index FAISS
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# 🔹 Vérifier que le dossier "data/" existe avant d'enregistrer FAISS
if not os.path.exists("data"):
    os.makedirs("data")

# 🔹 Sauvegarder l'index FAISS
faiss.write_index(index, "data/events_faiss.index")

# 🔹 Ajouter un ID unique à chaque événement et stocker les données utiles
df["ID"] = range(len(df))
df_mapping = df[["ID", "Nom", "Date", "Lieu", "Issue", "Résumé", "Conclusion", "Sections", "URL"]]
df_mapping.to_pickle("data/events_mapping.pkl")  # Stocker en Pickle pour un accès rapide

# 🔹 Ajouter une recherche hybride avec TF-IDF
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df["Texte_Indexé"])

# 🔹 Sauvegarder TF-IDF
pickle.dump(vectorizer, open("data/tfidf_vectorizer.pkl", "wb"))
pickle.dump(tfidf_matrix, open("data/tfidf_matrix.pkl", "wb"))

print("✅ Base vectorielle FAISS et TF-IDF créées avec succès !")