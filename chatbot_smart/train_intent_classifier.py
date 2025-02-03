import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# 🔹 1️⃣ Charger les données d'entraînement
df = pd.read_csv("intent_data_expanded.csv")

# 🔹 2️⃣ Transformer le texte en vecteurs numériques
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df["message"])  # Convertir le texte en vecteurs
y = df["intent"]  # Labels des intentions

# 🔹 3️⃣ Entraîner un modèle Naïve Bayes
classifier = MultinomialNB()
classifier.fit(X, y)

# 🔹 4️⃣ Sauvegarder le modèle et le vectorizer
joblib.dump(vectorizer, "vectorizer.pkl")
joblib.dump(classifier, "intent_classifier.pkl")

print("✅ Modèle d'intention entraîné et sauvegardé avec succès !")