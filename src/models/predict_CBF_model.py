import pandas as pd
import numpy as np

def recommandations_CBF(titre, mat_sim, num_recommendations = 10):

        # Import du jeu de données sur les films pour les titres
    df = pd.read_csv('./data/films.csv')

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

    return recommended_movies

titre = "Toy Story (1995)"
mat_sim = np.loadtxt("./data/sim_cos_CBF")

print(recommandations_CBF(titre, mat_sim, 5))