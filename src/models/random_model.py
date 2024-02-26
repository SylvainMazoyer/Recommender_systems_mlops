# Import des bibliothèques nécessaires
import pandas as pd
import random as rd

def random_recos(): 
    """retourne 5 films aléatoires de la liste movies.csv sous forme de dataframe"""


    # Import du jeu de données sur les films
    df_movies = pd.read_csv('./src/data/movies.csv')

    # nombre de films disponibles dans movies.csv
    nb_movies = len(df_movies)

    # réindexation car les moviesId ne vont pas de 1 à nb_movies
    df_movies.reset_index(inplace=True)

    # génération des recos sans graine pour obtenir des recos différentes à chaque fois
    list_recos = [rd.randrange(0,nb_movies) for i in range(5)]

    # récupération des films ainsi recommandés (aléatoirement)
    df_reco = df_movies[df_movies["index"].isin(list_recos)]

    return df_reco


