# Import des bibliothèques nécessaires
import pandas as pd
import random as rd
import psycopg2


def last_recos(): 
    """retourne les 5 derniers films ajoutés dans la table films """
    
    conn = psycopg2.connect(
        dbname='dataflix',
        user='postgres',
        password='dataflix',
        host='data_container', 
        port='5432'
    )

    cur = conn.cursor()
    cur.execute("SELECT * FROM films ORDER BY movieid DESC LIMIT 5")
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
    cur.close()
    conn.close()
    
    return df



