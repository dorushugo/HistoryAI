import requests
from bs4 import BeautifulSoup
import re

# URL de la page Wikipédia
url = "https://fr.wikipedia.org/wiki/Guerre_du_Colorado"

# Envoyer une requête GET
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # 📌 Titre de la guerre
    title = soup.find("h1").text.strip()

    # 📌 Extraction de l'infobox (tableau avec les infos générales)
    caption = soup.find("caption", string="Informations générales")  # Cherche le caption spécifique
    general_info = {}
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

    # 📌 Affichage des résultats
    print(f"📌 Titre : {title}\n")

    print("📅 Infos générales :")
    for key, val in general_info.items():
        print(f"   - {key} : {val}")

    print("\n📖 Résumé :")
    print(summary[:1000] + "...")

    print("\n📖 Conclusion :")
    print(conclusion_text[:1000] + "...")

    print(f"\n📚 Sections principales : {', '.join(sections)}")