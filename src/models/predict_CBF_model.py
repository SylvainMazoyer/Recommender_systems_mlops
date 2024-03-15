import pandas as pd
import numpy as np

def recommandations_CBF(df_films, titre, mat_sim, num_recommendations = 10):

        #  Créer une série d'indices en utilisant la colonne 'title' comme index
    indices = pd.Series(range(0,len(df_films)), index=df_films['title'])


        # On récupère l'indice associé au titre qui servira à identifier le livre dans la matrice de similarité
    idx = indices[titre]

        # On obtient les scores de similarité de tous les livres avec le livre donée et on les garde les tuples d'indice du livre et score dans une liste
    scores_similarite = list(enumerate(mat_sim[idx]))

        # On trie les livres en fonction des scores de similarité
    scores_similarite = sorted(scores_similarite, key=lambda x: x[1], reverse=True)

        # Obtenir les scores des 10 livres les plus similaires
    top_similair = scores_similarite[1:num_recommendations+1]

        # Obtenir les indices des livres
    res = [(indices.index[idx], score) for idx, score in top_similair]

        # Renvoyer les titres des films les plus similaires
    recommended_movies = [indices.index[idx] for idx, score in top_similair]

    #print(recommended_movies)

    results = df_films[df_films["title"] == recommended_movies[0]]

    for title in recommended_movies[1: len(recommended_movies)]:

        df_tmp = df_films[df_films["title"] == title]
        results = pd.concat([results, df_tmp], ignore_index=True)

    #results.reset_index(inplace=True)

    return results

"""from src.models.load_CBF_similarity_matrix import load_CBF_similarity_matrix
mat_sim = load_CBF_similarity_matrix()
films_path = './data/films.csv'
df_films = pd.read_csv(films_path)
title = df_films[df_films["movieId"] == 1]["title"].iloc[0]

reco = recommandations_CBF(df_films, title, mat_sim, num_recommendations = 5)

print(reco)

import json
results_json = reco.to_json(orient="records")

r = json.loads(results_json)
print(r)"""