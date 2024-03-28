import pandas as pd
import csv
import warnings
warnings.filterwarnings("ignore")

# Import du jeu de données sur les ratings des tous les films par les users
df_ratings = pd.read_csv('./data/ratings.csv')

"""Sélection des 3000 films les plus notés et enregistrement de leurs ratings dans notes.csv"""

# count des notations pour chaque film et tri descendant
df_ratings_grp = df_ratings.groupby('movieId').count()
df_ratings_grp = df_ratings_grp.sort_values(by='userId', ascending=False)

# Sélection des 3000 films les plus notés 
df_ratings_slct = df_ratings_grp.iloc[:3000]
df_ratings_slct.reset_index(inplace=True)
df_ratings_slct = df_ratings_slct["movieId"]
list_movies_slct = df_ratings_slct.to_list()

# création de la table ratings pour les 3000 films sélectionnés
df_ratings_3000 = df_ratings[df_ratings["movieId"].isin(list_movies_slct)]

# Enregistrement de cette table 
df_ratings_3000.to_csv('./data/notes.csv', index=True)

""" création de la table films.csv sur la base de movies.csv et en ajoutant les liens youtube"""

# Import du jeu de données sur les films
df_movies = pd.read_csv('./data/movies.csv')

# Import de la bdd sur les films contenant leurs liens youtube
df_links = pd.read_csv('./data/ml-youtube.csv')

# sélection des 3000 films en question
df_movies = df_movies[df_movies["movieId"].isin(list_movies_slct)]

# Génération du lien complet vers le trailer youtube
df_links["youtubeId"] = df_links["youtubeId"].apply(lambda x: 'https://www.youtube.com/watch?v='+x)

# renommage de la colonne Title pour éviter un doublon lors du merge
df_links.rename(columns={"title":"Title"}, inplace=True)

# Merge pour inclure les liens youtube dans df_movies
df_movies_full = df_movies.merge(df_links, on="movieId")

# Mise en forme du dataset 
df_movies_full.drop(columns=["Title"], inplace=True)

# Ecriture du fichier dans src/data
df_movies_full.to_csv("./data/films.csv", index=False)


"""Création de la liste des genres existants et enregistrement dans le fichier genres.dat"""

df_films = df_movies_full.copy()

df_genres = df_films.genres
df_genres = df_genres.apply(lambda x: ' '.join(x.split('|')))
list_genres = df_genres.tolist()
genres_str = ' '.join(list_genres)
genres_list_2 = genres_str.split(' ')
genres_set = set(genres_list_2)
genres_list3 = list(genres_set)

with open("./data/genres.dat", 'w', newline='') as myfile:
     wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
     wr.writerow(genres_list3)

"""Création de la table utilisateurs.csv avec l'id, le nom et le dernier film vu à partir de df_notes"""

df_notes =  df_ratings_3000.copy()

df_grp_by = df_notes.groupby(by=["userId"]).max()

list_timestamps = sorted(df_grp_by["timestamp"].to_list(), reverse=True)

df_utilisateurs = df_notes[df_notes["timestamp"].isin(list_timestamps)].drop_duplicates(subset=["userId","timestamp"])

df_utilisateurs = df_utilisateurs.sort_values(by="timestamp", ascending=False)

df_utilisateurs = df_utilisateurs.drop_duplicates(subset=["userId"])

df_utilisateurs = df_utilisateurs[["userId", "movieId"]]

df_utilisateurs.reset_index(drop=True, inplace=True)

df_utilisateurs["name"] = df_utilisateurs["userId"].apply(lambda x: "user"+str(x))

df_utilisateurs.rename(columns={"movieId": "last_viewed"}, inplace=True)

df_utilisateurs = df_utilisateurs[["userId", "name", "last_viewed"]]

df_utilisateurs.to_csv("./data/utilisateurs.csv", index=False)

print(len(df_utilisateurs))