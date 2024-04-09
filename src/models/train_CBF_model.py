import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import psycopg2



def train_CBF_model():
    # Import du jeu de données sur les films
    conn = psycopg2.connect(
        dbname='dataflix',
        user='postgres',
        password='dataflix',
        host='data_container', 
        port='5432'
    )

    cur = conn.cursor()
    cur.execute("SELECT * FROM films")
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
    cur.close()
    conn.close()

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
    np.savetxt("./sim_cos_CBF.txt", sim_cosinus)

