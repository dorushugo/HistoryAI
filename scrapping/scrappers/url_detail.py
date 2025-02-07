import requests
from bs4 import BeautifulSoup
import pandas as pd
import subprocess
import re

# Fonction pour récupérer les informations détaillées d'une guerre à partir de l'URL
def get_infos_guerre(url_guerre):
    response = requests.get(url_guerre)
    if response.status_code != 200:
        print(f"⚠️ Erreur lors de la récupération de la page : {url_guerre}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")

    # 📌 Titre de la guerre
    title = soup.find("h1").text.strip()

    # 📌 Extraction de l'infobox (tableau avec les infos générales)
    caption = soup.find("caption", string="Informations générales")  
    general_info = {}
    if caption:
        info_table = caption.find_parent("table")
        if info_table:
            rows = info_table.find_all("tr")  

            for row in rows:
                header = row.find("th")  
                value = row.find("td")   

                if header and value:
                    key = header.get_text(strip=True)

                    # 🔎 Gestion des balises <time> et <a>
                    if value.find("time"):
                        val = " - ".join(time.get_text(strip=True) for time in value.find_all("time"))
                    elif value.find("a"):
                        val = ", ".join(a.get_text(strip=True) for a in value.find_all("a"))
                    else:
                        val = value.get_text(strip=True)

                    general_info[key] = val

    # 📌 Extraction de tous les paragraphes du contenu
    paragraphs = [p.text.strip() for p in soup.find_all("p") if p.text.strip()]

    # 📖 Résumé = 3 premiers paragraphes
    summary = " ".join(paragraphs[:3])

    # 📖 Conclusion = 2 derniers paragraphes
    conclusion_text = " ".join(paragraphs[-2:])
    
    full_content = " ".join(paragraphs) 

    # 📚 Extraction des sections principales (sans "[modifier | modifier le code]")
    sections = [h2.text.strip().replace("[modifier | modifier le code]", "").strip() for h2 in soup.find_all("span", class_="mw-headline")]

    # Nettoyer les références et le mot "modifier" dans le contenu complet, résumé et conclusion
    full_content = re.sub(r'\[.*?\]', '', full_content)  # Supprimer les références entre crochets
    summary = re.sub(r'\[.*?\]', '', summary)
    conclusion_text = re.sub(r'\[.*?\]', '', conclusion_text)

    # Supprimer le mot "modifier" uniquement en début de ligne
    full_content = re.sub(r'^\s*modifier\b', '', full_content, flags=re.MULTILINE)
    summary = re.sub(r'^\s*modifier\b', '', summary, flags=re.MULTILINE)
    conclusion_text = re.sub(r'^\s*modifier\b', '', conclusion_text, flags=re.MULTILINE)

    # Retourner les informations extraites
    return {
        "Nom": title,
        "URL": url_guerre,
        "Date": general_info.get("Date", ""),
        "Lieu": general_info.get("Lieu", ""),
        "Issue": general_info.get("Issue", ""),
        "Résumé": summary,
        "Conclusion": conclusion_text,
        "Contenu_complet": full_content,  # Ajout du texte complet
        "Sections": ", ".join(sections)
    }


def clean_and_save_to_csv(guerres_details):
    # Nettoyage des données après récupération
    df = pd.DataFrame(guerres_details)

    # Suppression des références entre crochets dans toutes les colonnes
    for col in df.columns:
        df[col] = df[col].apply(lambda x: re.sub(r'\[.*?\]', '', str(x)))

    # Sauvegarder les données nettoyées dans un CSV
    df.to_csv("guerres_details_full_clean.csv", index=False, encoding="utf-8")
    print("✅ Données nettoyées et enregistrées dans 'guerres_details_full_clean.csv'.")


# Fonction principale pour récupérer les informations détaillées pour toutes les guerres
def main():
    print("Démarrage du script principal")

    # Étape 1: Récupérer les URLs des guerres via le premier scraper
    print("📡 Récupération des URLs des guerres...")
    subprocess.run(["python3", "scrapper_url.py"])

    # Charger le CSV contenant les URLs des guerres
    guerres_df = pd.read_csv("details_guerres.csv")

    guerres_details = []

    # Parcourir chaque guerre et récupérer les infos détaillées
    for index, row in guerres_df.iterrows():
        print(f"({index+1}/{len(guerres_df)}) 📝 Récupération des informations pour {row['Nom']}...")
        infos_guerre = get_infos_guerre(row["URL"])

        if infos_guerre:
            guerres_details.append(infos_guerre)
    
    clean_and_save_to_csv(guerres_details)

if __name__ == "__main__":
    main()


# url_test = "https://fr.wikipedia.org/wiki/Guerre_du_Colorado"
# infos_test = get_infos_guerre(url_test)

# # Vérification du contenu complet
# print(f"🔍 Nom: {infos_test['Nom']}")
# print(f"📖 Résumé: {infos_test['Résumé'][:500]}...")  # Afficher les 500 premiers caractères
# print(f"📖 Conclusion: {infos_test['Conclusion'][:500]}...")  
# print(f"📜 Contenu complet: {infos_test['Contenu_complet'][:1000]}...")  # Afficher les 1000 premiers caractères

# # Enregistrement en CSV pour vérifier
# pd.DataFrame([infos_test]).to_csv("test_guerre_colorado.csv", index=False, encoding="utf-8")

# print("✅ Test terminé, fichier 'test_guerre_colorado.csv' enregistré.")