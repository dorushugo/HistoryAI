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

# Supabase credentials
SUPABASE_URL = "https://ggjjbljpisptelylnczn.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdnampibGpwaXNwdGVseWxuY3puIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzgyMzQ2NDksImV4cCI6MjA1MzgxMDY0OX0.clHxFvCYKgudlO6J5u1df0NfN8qo5XpuRXa46XHbcQQ"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdnampibGpwaXNwdGVseWxuY3puIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczODIzNDY0OSwiZXhwIjoyMDUzODEwNjQ5fQ.VAKzwStH8XL1bZTOJXUKWszDjE0QpwRB0CYkQU39Xrk"

OPEN_AI_SECRET_KEY="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"

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

def scrape_war_summary(war_url, war_id):
    """
    Scrape Wikipedia page for a war and extract summary, name, date, and full content.

    Args:
        war_url (str): URL of the Wikipedia page for the war.
        war_id (int): Unique identifier for the war.

    Returns:
        dict: Dictionary containing war name, date, summary text, full content, and URL.
              Returns None if scraping fails.
    """
    print(f"Processus {multiprocessing.current_process().name} - Début du scraping de la page de guerre: {war_url}") # LOG: Ajout du nom du processus
    try:
        response = requests.get(war_url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, "html.parser")

        # 📌 Titre de la guerre
        war_name = soup.find("h1").text.strip()

        # 📌 Extraction de l'infobox (tableau avec les infos générales)
        caption = soup.find("caption", string="Informations générales")  # Cherche le caption spécifique
        general_info = {}
        info_table = None
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

        # Transformation de general_info en une seule chaîne de texte
        general_info_text = "; ".join(f"{key}: {value}" for key, value in general_info.items())

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

        # Extraction du contenu complet
        content_div = soup.select_one('div#mw-content-text > div.mw-parser-output')
        full_content = content_div.get_text(" ", strip=True) if content_div else "Contenu non trouvé"

        # Génération de l'embedding
        summary_embedding = get_embedding(summary) if summary else []

        # Construction des données
        war_data = {
            "id": war_id,
            "name": war_name,
            "general_info": general_info_text,
            "sections": sections,
            "summary": summary,
            "summary_embedding": summary_embedding,
            "conclusion": conclusion_text,
            "full_content": full_content,
            "url": war_url
        }

        # Affichage des résultats
        print("\n" + "="*50)
        print(f"📌 Titre : {war_data['name']}")
        print(f"🌍 Infos générales : {general_info_text[:100]}...")
        print(f"📚 Sections : {', '.join(sections[:3])}...")
        print(f"📖 Résumé ({len(summary)} caractères) : {summary[:200]}...")
        print("="*50 + "\n")

        return war_data

    except requests.exceptions.RequestException as e:
        print(f"Processus {multiprocessing.current_process().name} - Erreur de requête HTTP lors de la récupération de l'URL {war_url}: {e}") # LOG: Ajout du nom du processus
        return None
    except Exception as e:
        print(f"Processus {multiprocessing.current_process().name} - Erreur lors du traitement de l'URL {war_url}: {e}") # LOG: Ajout du nom du processus
        return None


def get_list_of_wars_urls(list_page_url):
    """
    Scrape a Wikipedia list page to get URLs of war pages.

    Args:
        list_page_url (str): URL of the Wikipedia page listing wars.

    Returns:
        list: List of Wikipedia URLs for wars.
    """
    print(f"Début de la récupération de la liste des URLs de guerres depuis: {list_page_url}") # LOG: Début récupération liste URLs
    try:
        response = requests.get(list_page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        war_urls = []
        # Adjust selector based on the structure of the list page
        list_items = soup.select('div#mw-content-text div.mw-parser-output ul li a[href^="/wiki/"]') # Common list format
        for item in list_items:
            war_page_url = "https://fr.wikipedia.org" + item['href']
            if "/wiki/Liste_de" not in war_page_url and "/wiki/Guerre_" in war_page_url: # Filter out list pages and keep only war pages (heuristic)
                 war_urls.append(war_page_url)

        print("URLs de guerres trouvées :", war_urls) # LOG: URLs de guerres trouvées
        print(f"Liste des URLs de guerres récupérée avec succès depuis: {list_page_url}") # LOG: Fin récupération liste URLs
        return war_urls

    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête HTTP lors de la récupération de la page de liste {list_page_url}: {e}")
        return []
    except Exception as e:
        print(f"Erreur lors du traitement de la page de liste {list_page_url}: {e}")
        return []


def test_supabase_connection():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        result = supabase.table('wars').select("count", count="exact").execute()
        print("✅ Connexion à Supabase réussie")
        print(f"Nombre d'entrées dans la table : {result.count}")
    except Exception as e:
        print(f"🚨 Erreur de connexion : {str(e)}")
        exit()


if __name__ == "__main__":
    test_supabase_connection()
    list_of_wars_page_url = "https://fr.wikipedia.org/wiki/Liste_des_guerres"
    print(f"URL de la page de liste des guerres utilisée: {list_of_wars_page_url}")
    war_urls = get_list_of_wars_urls(list_of_wars_page_url)

    if war_urls:
        all_wars_data = []
        print(f"Début du scraping des pages de guerres en parallèle avec multiprocessing...")

        with multiprocessing.Pool() as pool:
            results = pool.starmap(scrape_war_summary, [(url, i) for i, url in enumerate(war_urls)])

        all_wars_data = [war_data for war_data in results if war_data]

        print(f"Fin du scraping. Début de l'insertion dans Supabase...")

        # Initialisation du client Supabase avec vérification
        try:
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            print("Connexion à Supabase réussie")
        except Exception as e:
            print(f"Échec de la connexion à Supabase : {str(e)}")
            exit()

        # Vérification de l'existence de la table
        try:
            test = supabase.table("wars").select("count", count="exact").execute()
            print("La table 'wars' existe bien")
        except Exception as e:
            print(f"La table 'wars' n'existe pas ou erreur d'accès : {str(e)}")
            exit()

        # Insertion des données avec meilleure gestion d'erreur
        for war in all_wars_data:
            try:
                # Convertir les listes en JSON
                war['sections'] = json.dumps(war.get('sections', []))
                
                # Nettoyer les textes
                for key in ['summary', 'conclusion', 'full_content']:
                    if key in war:
                        war[key] = war[key].encode('utf-8', 'ignore').decode('utf-8')

                # Debug: Afficher les données avant insertion
                print(f"Données à insérer : {json.dumps(war, indent=2, ensure_ascii=False)}")
                
                # Insertion
                if 'summary_embedding' in war and war['summary_embedding']:
                    war['summary_embedding'] = np.array(war['summary_embedding']).tolist()
                data, count = supabase.table("wars").insert(war).execute()
                print(f"✅ Insertion réussie : {war['name']}")

            except Exception as e:
                print(f"🚨 Erreur d'insertion : {str(e)}")
                if hasattr(e, 'args') and len(e.args) > 0:
                    print(f"Détails de l'erreur : {e.args[0]}")
                continue

        print("Insertion terminée avec succès !")

    else:
        print("Aucune URL de guerre trouvée.")
    print("Script terminé.")
