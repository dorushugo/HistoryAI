import pandas as pd
import random

# 🔹 Liste des intents existants
intents = ["quizz", "quizz_reponses", "résumé", "recherche"]

# 🔹 Liste de sujets historiques courants
sujets_histoire = test_messages = [
    "la Guerre de la Ligue de Cambrai", "la Guerre de Trente Ans", "la Guerre de Dévolution",
    "la Guerre de Hollande", "la Guerre de la Ligue d'Augsbourg", "la Guerre de Succession d'Espagne",
    "la Guerre de la Quadruple-Alliance", "la Guerre de Succession de Pologne", "la Guerre de Succession d'Autriche",
    "la Guerre de Sept Ans", "la Guerre d'Indépendance des États-Unis", "les Guerres de la Révolution française",
    "les Guerres napoléoniennes", "la Guerre de 1812", "la Guerre d'indépendance grecque",
    "la Guerre de Crimée", "la Guerre de Sécession", "la Guerre franco-prussienne",
    "la Guerre des Boers", "Première la Guerre mondiale", "la Guerre civile russe",
    "la Guerre d'indépendance irlandaise", "la Guerre civile chinoise", "la Guerre d'Espagne",
    "Seconde Guerre mondiale", "la Guerre de Corée", "la Guerre d'Algérie",
    "la Guerre du Vietnam", "la Guerre du Yom Kippour", "la Guerre d'Afghanistan",
    "la Guerre Iran-Irak", "la Guerre du Golfe", "la Guerre de Bosnie",
    "la Guerre du Kosovo", "la Guerre d'Irak", "la Guerre civile syrienne",
    "la Guerre du Donbass", "la Guerre du Haut-Karabagh", "la Guerre civile libyenne",
    "la Guerre civile yéménite", "la Guerre du Mali", "la Guerre civile centrafricaine",
    "la Guerre du Darfour", "la Guerre civile sud-soudanaise", "la Guerre du Tigré",
    "la Guerre civile éthiopienne", "la Guerre civile angolaise", "la Guerre civile mozambicaine",
    "la Guerre civile sierra-léonaise", "la Guerre civile libérienne"
]

# 🔹 Modèles de phrases pour chaque intent
modeles = {
    "quizz": [
        "Peux-tu me faire un quizz sur {} ?", "J’aimerais un quiz sur {}",
        "Fais-moi un quizz sur {}", "Génère un quizz sur {}", "Je veux un quizz sur {}",
        "Test mes connaissances sur {}", "Pose-moi des questions sur {}"
    ],
    "quizz_reponses": [
        "Quelles sont les réponses du dernier quizz ?", "Peux-tu me donner les corrigés du quizz ?",
        "J’aimerais voir les réponses du quizz", "Affiche-moi les réponses du test",
        "Donne-moi les solutions aux questions posées"
    ],
    "résumé": [
        "Donne-moi un résumé de {}", "Fais-moi un résumé sur {}", "Je veux une fiche de révision sur {}",
        "Explique-moi en bref {}", "Je veux un résumé sur {}", "Raconte-moi en quelques phrases {}",
        "Fais-moi une synthèse sur {}"
    ],
    "recherche": [
        "Que s’est-il passé en {} ?", "Parle-moi de {}", "Quels sont les événements de {} ?",
        "Quand a eu lieu {} ?", "Quels sont les faits marquants de {} ?", "Donne-moi des informations sur {}",
        "Quels sont les événements majeurs de {} ?", "Explique-moi ce qu'était {}",
        "Quelles sont les causes de {} ?", "Quels pays étaient impliqués dans {} ?",
        "Raconte-moi l'histoire de {}", "Explique-moi {}", "Quels sont les événements clés de {} ?",
        "Quand a commencé {} ?", "Quels sont les empires ayant existé en {} ?",
        "Dis-moi tout ce que tu sais sur {}", "J’aimerais apprendre plus sur {}",
        "Quels sont les faits historiques les plus importants de {} ?", "Raconte-moi une anecdote sur {}",
        "Explique-moi une bataille célèbre liée à {}", "Peux-tu me parler d’un événement marquant de {} ?",
        "Fais-moi un exposé sur un grand personnage de {}", "Quels sont les conflits les plus meurtriers de {} ?",
        "Quels sont les personnages célèbres de {} ?"
    ]
}

# 🔹 Générer 10 000 lignes de données
dataset = []
for _ in range(10000):
    intent = random.choice(intents)  
    sujet = random.choice(sujets_histoire)  
    phrase = random.choice(modeles[intent]).format(sujet)  
    dataset.append((phrase, intent))

# 🔹 Convertir en DataFrame et sauvegarder
df_expanded = pd.DataFrame(dataset, columns=["message", "intent"])
df_expanded.to_csv("intent_data_expanded.csv", index=False, encoding="utf-8")

print("✅ Fichier intent_data_expanded.csv généré avec succès !")