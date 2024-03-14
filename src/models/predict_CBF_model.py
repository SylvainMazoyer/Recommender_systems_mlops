import pandas as pd
import numpy as np

def recommandations_CBF(df, titre, mat_sim, num_recommendations = 10):

        #  Créer une série d'indices en utilisant la colonne 'title' comme index
    indices = pd.Series(range(0,len(df)), index=df['title'])


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

    reco = {}

    for i in range(0, 5):

        movieId = df[df["title"] == recommended_movies[i]]["movieId"].iloc[0]
        reco[movieId] = recommended_movies[i]

    return reco