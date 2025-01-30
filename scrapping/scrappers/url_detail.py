import requests
from bs4 import BeautifulSoup
import pandas as pd

# Fonction pour récupérer les informations détaillées d'une guerre à partir de l'URL
def get_infos_guerre(url_guerre):
    response = requests.get(url_guerre)
    if response.status_code != 200:
        print(f"⚠️ Erreur lors de la récupération de la page de la guerre: {url_guerre}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")

    # 📌 Titre de la guerre
    title = soup.find("h1").text.strip()

    # 📌 Extraction de l'infobox (tableau avec les infos générales)
    caption = soup.find("caption", string="Informations générales")  # Cherche le caption spécifique
    general_info = {}
    if caption:
        info_table = caption.find_parent("table")
        if info_table:
            rows = info_table.find_all("tr")  # Trouver toutes les lignes du tableau

            for row in rows:
                header = row.find("th")  # Colonne de gauche (nom de l'info)
                value = row.find("td")   # Colonne de droite (valeur associée)

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

    # 📌 Extraction des paragraphes
    paragraphs = [p.text.strip() for p in soup.find_all("p") if p.text.strip()]

    # 📖 Résumé = 3 premiers paragraphes
    summary = " ".join(paragraphs[:3])

    # 📖 Conclusion = 2-3 derniers paragraphes (en évitant les références)
    last_paragraphs = paragraphs[-5:]
    conclusion = []
    for para in reversed(last_paragraphs):
        if len(conclusion) < 3:
            conclusion.insert(0, para)

    conclusion_text = " ".join(conclusion)

    # 📚 Extraction des sections principales (sans "[modifier | modifier le code]")
    sections = [h2.text.strip().replace("[modifier | modifier le code]", "").strip() for h2 in soup.find_all("div", class_="mw-heading mw-heading2")]

    # Retourner les informations extraites
    return {
        "Nom": title,
        "URL": url_guerre,
        "Date": general_info.get("Date", ""),
        "Lieu": general_info.get("Lieu", ""),
        "Issue": general_info.get("Issue", ""),
        "Résumé": summary,
        "Conclusion": conclusion_text,
        "Sections": ", ".join(sections)
    }


# Fonction principale pour récupérer les informations détaillées pour toutes les guerres
def main():
    # Charger le CSV contenant les URLs des guerres
    guerres_df = pd.read_csv("details_guerres.csv")

    guerres_details = []

    # Parcourir chaque guerre et récupérer les infos détaillées
    for index, row in guerres_df.iterrows():
        print(f"📝 Récupération des informations pour {row['Nom']}...")
        infos_guerre = get_infos_guerre(row["URL"])
        if infos_guerre:
            guerres_details.append(infos_guerre)

    # Sauvegarder les informations détaillées dans un fichier CSV
    details_df = pd.DataFrame(guerres_details)
    details_df.to_csv("guerres_details_completes.csv", index=False, encoding="utf-8")
    print("✅ Données détaillées enregistrées dans 'guerres_details_completes.csv'.")


if __name__ == "__main__":
    main()
