import subprocess
import pandas as pd
from scrappers.url_detail import get_infos_guerre  # Importation de la fonction pour récupérer les infos détaillées
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

def main():
    print("Démarrage du script principal")
    # Ton code principal ici

    # Étape 1: Récupérer les URLs des guerres via le premier scraper
    print("📡 Récupération des URLs des guerres...")
    subprocess.run(["python3", "scrappers/scrapper_url.py"])

    # Étape 2: Charger les URLs récupérées dans le fichier CSV
    guerres_df = pd.read_csv("details_guerres.csv")

    guerres_details = []

    # Étape 3: Récupérer les informations détaillées pour chaque guerre
    print("📝 Récupération des informations détaillées...")
    for index, row in guerres_df.iterrows():
        print(f"📝 Récupération des informations pour {row['Nom']}...")
        infos_guerre = get_infos_guerre(row["URL"])
        if infos_guerre:
            guerres_details.append(infos_guerre)

    # Étape 4: Sauvegarder les informations détaillées dans un CSV
    details_df = pd.DataFrame(guerres_details)
    details_df.to_csv("guerres_details_completes.csv", index=False, encoding="utf-8")
    print("✅ Données détaillées enregistrées dans 'guerres_details_completes.csv'.")
    return details_df

if __name__ == "__main__":
    df = main()

    # 🔥 CHOISIR UN MODÈLE MULTILINGUE POUR LE FRANÇAIS
    model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    # Vérification des colonnes attendues
    colonnes_attendues = ["Nom", "URL", "Date", "Lieu", "Issue", "Résumé", "Conclusion", "Sections"]
    for col in colonnes_attendues:
        if col not in df.columns:
            raise ValueError(f"⚠️ La colonne '{col}' est absente du DataFrame ! Vérifie tes données.")

    # Remplir les valeurs manquantes pour éviter les erreurs
    df.fillna("Non renseigné", inplace=True)

    # # AMZELIORATION A TESTER POUR LE FUTUR, EN AJOUTANT UN CHAMP POUR FAIRE L'EMBEDDING DES 3 CHAMPS AU LIEU DE QUE RESUMÉ
    # # 🔹 Générer des descriptions enrichies (Nom + Date + Résumé)
    # df["Texte_Indexé"] = df["Nom"] + " " + df["Date"] + " " + df["Résumé"]

    # # 🔹 Générer des embeddings pour ce texte enrichi
    # descriptions = df["Texte_Indexé"].tolist()
    # embeddings = model.encode(descriptions)

    # 🔹 Générer des embeddings pour la colonne `Résumé`
    descriptions = df["Résumé"].tolist()
    embeddings = model.encode(descriptions)

    # 🔹 Créer l'index FAISS
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))  # Ajouter les vecteurs FAISS

    # 🔹 Sauvegarder l'index FAISS
    faiss.write_index(index, "data/events_faiss.index")

    # 🔹 Ajouter un ID unique à chaque événement et stocker les données utiles
    df["ID"] = range(len(df))
    df_mapping = df[["ID", "Nom", "Date", "Lieu", "Issue", "Résumé", "Conclusion", "Sections", "URL"]]
    df_mapping.to_pickle("data/events_mapping.pkl")  # Stocker en Pickle pour un accès rapide

    print("✅ Base vectorielle créée avec succès à partir du DataFrame !")