import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import du jeu de données sur les films dans le répertoire data à la racine du projet
df = pd.read_csv('./data/movies.csv')

# formattage de la colonne genre
df['Genres'] = df['genres'].apply(lambda x: ' '.join(x.split('|')))

# formattage de la colonne title avec suppression de la date 
df['Title'] = df["title"].apply(lambda x:x[:-6])

# création de la colonne descriptive de l'ensemble du film
df['Description'] = df['Title'] + df['Genres']

# Créer un TfidfVectorizer et supprimer les mots vides
tfidf = TfidfVectorizer(stop_words='english')

# Adapter et transformer les données en une matrice tfidf
matrice_tfidf = tfidf.fit_transform(df['Description'])

# On calcule la similarité cosinus
sim_cosinus = cosine_similarity(matrice_tfidf, matrice_tfidf)

# Créer une série d'indices en utilisant la colonne 'title' comme index
indices = pd.Series(range(0,len(df)), index=df['title'])


