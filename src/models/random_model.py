# Import des bibliothèques nécessaires
import pandas as pd
import random as rd
import psycopg2


def random_recos(): 
    """retourne 5 films aléatoires de la liste films.csv sous forme de dataframe"""
    
    conn = psycopg2.connect(
        dbname='dataflix',
        user='postgres',
        password='dataflix',
        host='data_container', 
        port='5432'
    )

    cur = conn.cursor()
    cur.execute("SELECT * FROM films ORDER BY RANDOM() LIMIT 5")
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
    cur.close()
    conn.close()
    
    return df


"""print(random_recos())"""


