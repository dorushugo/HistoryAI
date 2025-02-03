import pandas as pd
import random

# 🔹 Liste des intents existants
intents = ["quizz", "quizz_reponses", "résumé", "détail"]

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
        "Test mes connaissances sur {}", "Pose-moi des questions sur {}","Peux-tu me préparer un quizz sur {} ?",
        "J’aimerais répondre à un quizz sur {}", "Crée-moi un quizz sur {}", "Génère quelques questions sur {}",
        "Je veux tester mes connaissances sur {}", "Lance-moi un quizz sur {}", "Donne-moi des questions sur {}",
        "Fais-moi un test de culture générale sur {}", "Peux-tu générer un quizz éducatif sur {} ?", "J’aimerais voir si je connais bien {}",
        "Évalue-moi avec un quizz sur {}", "As-tu un quizz à me proposer sur {} ?", "Je veux m’entraîner avec un quizz sur {}", "Crée-moi 5 questions sur {}",
        "Génère un questionnaire sur {}", "Teste-moi avec des questions sur {}", "Peux-tu me poser une série de questions sur {} ?",
        "Je veux répondre à des questions sur {}", "Prépare-moi un petit jeu de questions sur {}","Fais-moi un test interactif sur {}"
    ],
    "quizz_reponses": [
        "Quelles sont les réponses du dernier quizz ?", "Peux-tu me donner les corrigés du quizz ?",
        "J’aimerais voir les réponses du quizz", "Affiche-moi les réponses du test",
        "Donne-moi les solutions aux questions posées", "Quelles sont les réponses du dernier quizz ?",
        "Quels étaient les bonnes réponses au quizz ?", "Montre-moi les réponses du dernier test",
        "Je veux voir les bonnes réponses au quizz", "Peux-tu me montrer les corrections du quizz ?",
        "Affiche-moi le corrigé des questions", "J’aimerais voir les réponses aux questions du quizz",
        "Rappelle-moi les réponses aux questions que tu as posées", "Donne-moi le corrigé du test que j’ai fait",
        "Peux-tu m’envoyer les bonnes réponses aux questions ?",
        "J’aimerais comparer mes réponses avec le corrigé", "Je veux savoir si mes réponses au quizz étaient correctes",
        "Montre-moi où je me suis trompé dans le quizz", "Peux-tu me dire quelles réponses étaient justes ?",
        "Je veux vérifier mes réponses au dernier test","Affiche les solutions du quizz que j’ai fait"
    ],
    "résumé": [
        "Donne-moi un résumé détaillé sur {}", "Fais-moi une fiche de révision complète sur {}",
        "Je veux une fiche de synthèse pour réviser {}", "Explique-moi les points essentiels de {}",
        "Récapitule-moi les faits importants de {}", "Fais-moi un résumé structuré sur {}",
        "J’ai besoin d’une synthèse pour apprendre {}", "Peux-tu me préparer un mémo récapitulatif sur {} ?",
        "Fais-moi un plan détaillé des événements de {}", "Quels sont les éléments clés à retenir sur {} ?",
        "Je veux une fiche récapitulative sur {}", "Aide-moi à comprendre rapidement {}",
        "Raconte-moi les grandes lignes de {}", "Peux-tu me faire une fiche de cours sur {} ?",
        "Fais-moi une révision express de {}", "Quels sont les concepts importants de {} ?",
        "J’ai un examen, donne-moi une synthèse sur {}", "Je veux une explication courte mais claire sur {}",
        "Peux-tu me faire une fiche de révision avec les points essentiels de {} ?", "Quels sont les points à absolument retenir sur {} ?",
        "Quels sont les éléments les plus importants à savoir sur {} ?", "Quels sont les principaux événements liés à {} ?",
    ],
    "détail": [
    "Peux-tu m'expliquer en détail {} ?", "J’aimerais une analyse approfondie sur {}", "Fais-moi une présentation complète de {}",
    "Explique-moi {} en profondeur", "Quels sont les aspects les plus complexes de {} ?",
    "Peux-tu me donner un cours détaillé sur {} ?", "Quels sont les enjeux politiques et économiques de {} ?",
    "Raconte-moi toute l’histoire de {} avec un maximum de détails", "Quels ont été les impacts de {} à long terme ?",
    "Quels étaient les objectifs des acteurs impliqués dans {} ?", "Explique-moi comment {} a évolué au fil du temps",
    "Quels sont les faits méconnus à propos de {} ?", "Peux-tu me faire une analyse historique sur {} ?",
    "Quelles sont les différentes théories sur {} ?",
    "Quels sont les documents et sources historiques sur {} ?", "Quelles sont les controverses liées à {} ?",
    "Quels liens peut-on faire entre {} et d'autres événements historiques ?",
    "Quels ont été les facteurs déclencheurs de {} ?",
    "Peux-tu me détailler les différentes phases de {} ?",
    "Quelle est l’importance de {} dans l’histoire ?",
    "Quels personnages ont joué un rôle clé dans {} ?",
    "Explique-moi comment {} a influencé le monde moderne",
    "Quels ont été les impacts sociaux et culturels de {} ?",
    "Quels étaient les stratégies militaires utilisées lors de {} ?",
    "Quels ont été les principaux acteurs impliqués dans {} ?",
    "Comment {} a changé la géopolitique mondiale ?",
    "Quels ont été les défis et les conséquences de {} ?",
    "Comment les historiens analysent-ils aujourd’hui {} ?",
    "Peux-tu faire une comparaison entre {} et un autre événement similaire ?",
    "Quels étaient les tensions internationales autour de {} ?",
    "Quelle a été l'influence des médias sur {} ?",
    "Quels étaient les opinions et réactions des populations face à {} ?",
    "Quels sont les mythes et idées reçues sur {} ?",
    "Peux-tu me raconter des anecdotes intéressantes sur {} ?",
    "Comment {} a-t-il été enseigné et perçu dans différentes époques ?",
    "Quels ont été les principaux changements politiques après {} ?",
    "Quelle est la perception actuelle de {} dans le monde ?",
    "Quels parallèles peut-on faire entre {} et des événements récents ?"
]
}

# 🔹 Générer 100 000 lignes de données
dataset = []
for _ in range(100000):
    intent = random.choice(intents)  
    sujet = random.choice(sujets_histoire)  
    phrase = random.choice(modeles[intent]).format(sujet)  
    dataset.append((phrase, intent))

# 🔹 Convertir en DataFrame et sauvegarder
df_expanded = pd.DataFrame(dataset, columns=["message", "intent"])
df_expanded.to_csv("intent_data_expanded.csv", index=False, encoding="utf-8")

print("✅ Fichier intent_data_expanded.csv généré avec succès !")