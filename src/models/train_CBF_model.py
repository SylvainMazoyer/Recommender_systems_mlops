import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tabulate import tabulate

# Import du jeu de données sur les films
df = pd.read_csv('../data/movies.csv')

# formattage de la colonne genre
df['Genres'] = df['genres'].apply(lambda x: ' '.join(x.split('|')))

# formattage de la colonne title avec suppression de la date 
df['Title'] = df["title"].apply(lambda x:x[:-6])

# création de la colonne descriptive de l'ensemble du film
df['Description'] = df['Title'] + df['Genres']