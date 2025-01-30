import subprocess
import pandas as pd
from scrappers.url_detail import get_infos_guerre  # Importation de la fonction pour récupérer les infos détaillées

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

if __name__ == "__main__":
    main()