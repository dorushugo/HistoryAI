import os
import faiss
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

# 🔹 Charger les données
df = pd.read_csv("guerres_details_full_clean.csv")

# 🔹 Remplacer NaN par une valeur par défaut
df.fillna("", inplace=True)

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

# 🔹 Initialiser le modèle d'embedding en français
# model = SentenceTransformer("dangvantuan/sentence-camembert-large")
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")


# 🔹 Générer les embeddings
descriptions = df["Texte_Indexé"].tolist()
embeddings = model.encode(descriptions)

# 🔹 Créer l'index FAISS
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# 🔹 Sauvegarder l'index FAISS
if not os.path.exists("data"):
    os.makedirs("data")

faiss.write_index(index, "data/guerres_faiss.index")

# 🔹 Sauvegarder le mapping des guerres
df["ID"] = range(len(df))
df_mapping = df[["ID", "Nom", "Date", "Lieu", "Issue", "Résumé", "Conclusion", "Sections", "URL"]]
df_mapping.to_pickle("data/guerres_mapping.pkl")

print("✅ Base vectorielle mise à jour avec succès !")