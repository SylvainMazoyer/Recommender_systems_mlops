import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import du jeu de données sur les films dans le répertoire data à la racine du projet
df = pd.read_csv('./data/films.csv')

# formattage de la colonne genre
df['Genres'] = df['genres'].apply(lambda x: ' '.join(x.split('|')))

# création de la colonne descriptive de l'ensemble du film
df['Description'] = df['title'] + " " + df['Genres']

# Créer un TfidfVectorizer et supprimer les mots vides
tfidf = TfidfVectorizer(stop_words='english')

# Adapter et transformer les données en une matrice tfidf
matrice_tfidf = tfidf.fit_transform(df['Description'])

# On calcule la similarité cosinus
sim_cosinus = cosine_similarity(matrice_tfidf, matrice_tfidf)

# conversion du type de la similarité cosinus en float16 pour améliorer le temps de chargement de cette matrice pour faire les prédictions
sim_cosinus = sim_cosinus.astype('float16')

# enregistrement dans un fichier
np.savetxt("./data/sim_cos_CBF", sim_cosinus)


