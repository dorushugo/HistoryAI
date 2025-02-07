import requests
from bs4 import BeautifulSoup
import csv # Importation du module csv
import multiprocessing # Importation du module multiprocessing
import re # Importation du module re
from supabase import create_client, Client
import os
import json
from openai import OpenAI
import numpy as np
import pandas as pd

# Supabase credentials
SUPABASE_URL = "https://ggjjbljpisptelylnczn.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdnampibGpwaXNwdGVseWxuY3puIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczODIzNDY0OSwiZXhwIjoyMDUzODEwNjQ5fQ.VAKzwStH8XL1bZTOJXUKWszDjE0QpwRB0CYkQU39Xrk"

OPEN_AI_SECRET_KEY = "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"

# Initialiser le client OpenAI
client = OpenAI(api_key=OPEN_AI_SECRET_KEY)

def get_embedding(text: str) -> list[float]:
    """Génère un embedding pour le texte donné en utilisant OpenAI"""
    try:
        # Limiter la taille du texte à 8191 tokens (limite du modèle)
        truncated_text = text[:8000]
        response = client.embeddings.create(
            input=truncated_text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Erreur lors de la génération de l'embedding : {str(e)}")
        return []

def get_infos_guerre(url_guerre, url_id):
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
    sections = [h2.text.strip().replace("[modifier | modifier le code]", "").strip() for h2 in soup.find_all("div", class_="mw-heading mw-heading2")]

    # Nettoyer les références et le mot "modifier" dans le contenu complet, résumé et conclusion
    full_content = re.sub(r'\[.*?\]', '', full_content)  # Supprimer les références entre crochets
    summary = re.sub(r'\[.*?\]', '', summary)
    conclusion_text = re.sub(r'\[.*?\]', '', conclusion_text)

    # Supprimer le mot "modifier" uniquement en début de ligne
    full_content = re.sub(r'^\s*modifier\b', '', full_content, flags=re.MULTILINE)
    summary = re.sub(r'^\s*modifier\b', '', summary, flags=re.MULTILINE)
    conclusion_text = re.sub(r'^\s*modifier\b', '', conclusion_text, flags=re.MULTILINE)

    # Générer l'embedding pour le titre et le contenu complet
    title_embedding = get_embedding(title)
    content_embedding = get_embedding(full_content)

    # Retourner les informations extraites
    war_data = {
        "id" : url_id,
        "nom": title,
        "url": url_guerre,
        "date": general_info.get("Date", ""),
        "lieu": general_info.get("Lieu", ""),
        "issue": general_info.get("Issue", ""),
        "résumé": summary,
        "conclusion": conclusion_text,
        "contenu_complet": full_content,  # Ajout du texte complet
        "sections": sections,
        "title_embedding": title_embedding,
        "content_embedding": content_embedding
    }
    
    # Affichage des résultats
    # print("\n" + "="*50)
    print(f"📌 Titre : {war_data['nom']}")
    print(f"🌍 Infos générales : {str(general_info)[:100]}...")
    print(f"📚 Sections : {', '.join(sections[:3])}...")
    print(f"📖 Résumé ({len(summary)} caractères) : {summary[:200]}...")
    # print("="*50 + "\n")
 
    return war_data

def get_guerre_lists(url_base):

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
                "nom": texte,
                "url": url_guerre
            })

    print(f"🔍 {len(guerres_urls)} guerres trouvées à scraper !")

    # Sauvegarde des données dans un fichier CSV
    df = pd.DataFrame(guerres_urls)

    # Supprimer les doublons basés sur la colonne "URL"
    df_clean = df.drop_duplicates(subset=["url"], keep="first")
    print(f"✅ Suppression des doublons terminée ! {len(df_clean)} guerres uniques enregistrées.")

    df_clean.to_csv("details_guerres.csv", index=False, encoding="utf-8")
    print("✅ Scraping terminé ! Données enregistrées dans 'details_guerres.csv'.")
    return df_clean

def test_supabase_connection():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        result = supabase.table('wars_test').select("count", count="exact").execute()
        print("La connexion Supabase fonctionne correctement.")
    except Exception as e:
        print(f"Erreur de connexion Supabase : {e}")

def insert_data(war_data):
    try:
        # Connexion à Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

        # Insérer les données dans la table 'wars_test'
        response = supabase.table('wars_test').insert(war_data).execute()
        print(f"✅ Données insérées avec succès : {war_data['nom']}")
    except Exception as e:
        print(f"Erreur lors de l'insertion des données dans Supabase : {e}")

if __name__ == "__main__":
    # Tester la connexion à Supabase
    test_supabase_connection()

    list_of_wars_page_url = "https://fr.wikipedia.org/wiki/Liste_des_guerres"
    print(f"URL de la page de liste des guerres utilisée: {list_of_wars_page_url}")

    # Récupérer les URLs des guerres
    war_df = get_guerre_lists(list_of_wars_page_url)
    war_urls = war_df["url"].tolist()

    if war_urls:
        all_wars_data = []
        print(f"🔄 Début du scraping des pages de guerres en parallèle avec multiprocessing...")

        # Multiprocessing pour accélérer le scraping
        with multiprocessing.Pool() as pool:
            results = pool.starmap(get_infos_guerre, [(url, i) for i, url in enumerate(war_urls)])

        # Filtrer les résultats valides
        all_wars_data = [war_data for war_data in results if war_data]

        print(f"✅ Fin du scraping. Début de l'insertion dans Supabase...")

        # Connexion unique à Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print("✅ Connexion à Supabase réussie")

        # Vérifier l'existence de la table
        try:
            test = supabase.table("wars_test").select("count", count="exact").execute()
            print("✅ La table 'wars_test' existe bien")
        except Exception as e:
            print(f"🚨 La table 'wars_test' n'existe pas ou erreur d'accès : {str(e)}")
            exit()

        # Insérer les données
        for war in all_wars_data:
            try:
                war['sections'] = json.dumps(war.get('sections', []))  # Sérialiser la liste en JSON
                
                # Nettoyage des champs texte
                for key in ['résumé', 'conclusion', 'contenu_complet']:
                    if key in war:
                        war[key] = war[key].encode('utf-8', 'ignore').decode('utf-8')

                # Convertir les embeddings en liste Python
                if 'title_embedding' in war and war['title_embedding']:
                    war['title_embedding'] = list(np.array(war['title_embedding']))
                if 'content_embedding' in war and war['content_embedding']:
                    war['content_embedding'] = list(np.array(war['content_embedding']))

                # Insertion dans Supabase
                data, count = supabase.table("wars_test").insert(war).execute()
                print(f"✅ Insertion réussie : {war['nom']}")

            except Exception as e:
                print(f"🚨 Erreur d'insertion pour {war['nom']} : {str(e)}")
                continue  # Passer à l'élément suivant

        print("✅ Insertion terminée avec succès !")
    else:
        print("⚠️ Aucune URL de guerre trouvée.")
    
    print("🎉 Script terminé.")
