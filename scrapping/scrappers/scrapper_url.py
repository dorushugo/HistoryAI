import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_guerre_lists():
    # URL de la page principale listant les guerres
    url_base = "https://fr.wikipedia.org/wiki/Liste_des_guerres"

    # Mots-clés à exclure dans les liens
    mots_a_exclure = ["Article", "Discussion", "Lire", "Modifier", "Voir", "Aide", "Historique", "Spécial",
                    "Liste", "Pages", "Catégorie", "Portail", "Projet", "Index","Citer"]

    # Effectuer la requête sur la page principale
    response = requests.get(url_base)
    if response.status_code != 200:
        print("⚠️ Erreur lors de la récupération de la page principale Wikipédia")
        exit()

    soup = BeautifulSoup(response.text, "html.parser")

    # Stocker les liens des guerres à scraper
    guerres_urls = []

    # Trouver toutes les listes de guerres et filtrer les liens inutiles
    for li in soup.select("li a"):
        lien = li.get("href")
        texte = li.text.strip()

        if lien and lien.startswith("/wiki/") and "guerre" in lien.lower():
            if any(mot.lower() in texte.lower() for mot in mots_a_exclure):
                continue  # Ignorer cette page si elle contient un mot exclu

            url_guerre = f"https://fr.wikipedia.org{lien}"
            guerres_urls.append({
                "Nom": texte,
                "URL": url_guerre
            })

    print(f"🔍 {len(guerres_urls)} guerres trouvées à scraper !")

    # Sauvegarde des données dans un fichier CSV
    df = pd.DataFrame(guerres_urls)

    # Supprimer les doublons basés sur la colonne "URL"
    df_clean = df.drop_duplicates(subset=["URL"], keep="first")
    print(f"✅ Suppression des doublons terminée ! {len(df_clean)} guerres uniques enregistrées.")

    df_clean.to_csv("details_guerres.csv", index=False, encoding="utf-8")
    print("✅ Scraping terminé ! Données enregistrées dans 'details_guerres.csv'.")
    return df_clean

    # Permet d'exécuter le script seul ou l'importer ailleurs
if __name__ == "__main__":
    urls = get_guerre_lists()