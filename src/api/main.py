from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn
from random_model import random_recos
from last_movies import last_recos
from train_CBF_model import train_CBF_model
from load_CBF_similarity_matrix import load_CBF_similarity_matrix
from predict_CBF_model import recommandations_CBF
from pydantic import BaseModel
import pandas as pd
import psycopg2
from typing import Optional
from passlib.context import CryptContext
import time
import logging 
import json
import threading 


# Configuration du logging
logging.basicConfig(filename='logs/API_log.log', encoding='utf-8', level=logging.INFO,
                    format='%(asctime)s : %(message)s', datefmt='%m/%d/%Y %H:%M:%S')


def wait_for_postgres(host, port, user, password, database, max_retries=10, retry_interval=10):
    retries = 0
    while retries < max_retries:
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            conn.close()
            print("PostgreSQL database is ready.")
            return
        except psycopg2.OperationalError as e:
            print(f"Connection to PostgreSQL failed: {e}")
            retries += 1
            time.sleep(retry_interval)
    
    raise Exception("Unable to connect to PostgreSQL database after multiple attempts.")

# 
wait_for_postgres(
    host='data_container',
    port=5432,
    user='postgres',
    password='dataflix',
    database='dataflix'
)
                    
# L'API ne se lane que si la base postgresql est disponible

api = FastAPI(
    title="API de recommandation de films",
    description="Le but est de proposer aux utilisateurs des films selon leurs goûts et préférences.",
    version="1.0.1",
    openapi_tags=[
    {
        'name': 'Home',
        'description': "Test de fonctionnement de l'API"
    },
    {
        'name': 'Utilisateurs',
        'description': 'fonctions sans authentification destinées aux utilisateurs de la plateforme'
    },
    {
        'name': 'Admin',
        'description': 'fonctions avec authentification destinées aux administrateurs de la plateforme et aux data scientists'
    }])

@api.get("/", tags=['Home'], name="Route test")
def read_root():
    """
    Retourne un message si l'API est accessible

    **Returns**:\n
        json : {"message": "API is functional"}
    """
    return {"message": "API is functional"}


train_CBF_model()
mat_sim = load_CBF_similarity_matrix()
mat_sim_lock = threading.Lock()

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
df_films = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
cur.close()
conn.close()
df_films_lock = threading.Lock()


security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



# Authentification admin simple
def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):

    """
    Vérifie les informations d'identification de l'administrateur.

    **Args**:\n
        credentials : Identification avec HTTPBasic()

    **Returns**:\n
        username (str) : nom de l'administrateur
        role (str) : role de l'administrateur

    **Raises**:\n
        HTTPException 401 : Si les informations d'identification sont incorrectes
    """

    conn = psycopg2.connect(
        dbname='dataflix',
        user='postgres',
        password='dataflix',
        host='data_container', 
        port='5432'
    )

    # Récupération des données du username dans la table admin
    cur = conn.cursor()
    cur.execute("SELECT admin_name, admin_password, admin_role FROM admins WHERE admin_name = %s", (credentials.username,))
    admin_record = cur.fetchone()
    cur.close()

    # Si l'utilisateur est présent dans la table admin, on vérifie son mot de passe
    if admin_record:
        db_name, db_password, db_role = admin_record
    
        # Si le mot de passe saisi ne correspond pas à celui de la base, on lève une erreur 
        if not (pwd_context.verify(credentials.password, db_password)):
            logging.info('%s : ERREUR 401 : Mot de passe incorrect', credentials.username)
            raise HTTPException(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Mot de passe incorrect",
                                headers={"WWW-Authenticate": "Basic"},
                            )

    # si le username n'est pas présent dans la table admin, on lève une erreur       
    else:
        logging.info('%s : ERREUR 401 : Admin inconnu', credentials.username)

        raise HTTPException(

                                status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Utilisateur inconnu",
                                headers={"WWW-Authenticate": "Basic"},
                            )

    conn.close()
    return credentials.username, db_role



@api.get("/admin/{asked_role}", tags=['Admin'], name="Authentification en tant qu'administrateur")
async def get_secure_data(asked_role, user_rights: tuple = Depends(verify_admin)):

    """

    Cette route renvoie un message de bienvenue lors de l'authentification.

    **Args**:\n
        - user_rights (tuple): (name, role) dépendant de verify_admin
        - asked_role (str) : rôle pour lequel l'administrateur souhaite se connecter

    **Returns**: \n
        json

    **Example** : \n
        Exemple de sortie : {"message": "Bonjour Dataflix, vous êtes connecté(e) en tant qu'administrateur"}

    **Raises**:\n
        HTTPException 401: Si l'administrateur demande des accès pour un rôle autre que le sien
    """
    username, role = user_rights

    if asked_role == 'Data' and role!='Data':
        logging.info('%s : ERREUR 401 : Droits insuffisants', username)
        raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Droits insuffisants",
                        headers={"WWW-Authenticate": "Basic"},
                    )
    logging.info('%s : Accès admin autorisé', username)
    return {"message": f"Bonjour {username}, vous êtes connecté(e) en tant qu'administrateur"}



class CreateUser(BaseModel):
    name: str


@api.post("/create-user", tags=['Utilisateurs'], name="Création/identification du userid")
def create_user(user_data: CreateUser):
    """
    Crée un nouvel utilisateur dans le système.

    **Args**:\n
        user_data (CreateUser): Instance du modèle pydantic CreateUser

    **Does**:\n
        - si l'utilisateur n'existe pas, ajout de ce dernier en base
        - si l'utilisateur existe, renvoi de son userid

    **Returns**:\n
        json:  
            - message
            - userId

    **Examples**: \n
        - {"message": "user created successfully", "userId": 2200}

    """

    new_user = user_data.model_dump()
    
    # Connexion à la base postgre
    conn = psycopg2.connect(
        dbname='dataflix',
        user='postgres',
        password='dataflix',
        host='data_container', 
        port='5432'
    )

    # Récupération de la ligne correspondant au user dans la table utilisateurs
    cur = conn.cursor()
    cur.execute("SELECT userId FROM utilisateurs where name_user = %s", (new_user['name'],))
    rows = cur.fetchone()
    cur.close()

    # Si aucune ligne ne remonte, on crée la personne
    if rows is None : 
        cur = conn.cursor()
        cur.execute("INSERT INTO utilisateurs (name_user) VALUES (%s)", (new_user['name'],))
        conn.commit()
        cur.close()

        cur = conn.cursor()
        cur.execute("SELECT userId FROM utilisateurs where name_user = %s", (new_user['name'],))
        rows = cur.fetchone()
        
        response = {"message": "user created successfully", "userId": rows[0]}
        logging.info('%s : Accès API POST /create-user : user créé', rows[0])

        cur.close()

    # Si une ligne remonte, on ne fait rien
    else:
        response = {"message": "user already exists", "userId": rows[0]}
        logging.info('%s : Accès API POST /create-user : user déjà existant', rows[0])
    
    conn.close()
    return response


class User_data(BaseModel):
    name: str
    id:int

@api.get("/predict/rand_model", tags=['Utilisateurs'],name="Sélection aléatoire de 5 films")
async def pred_rand_model(user_data: User_data):
    """
    Renvoie 5 films aléatoires parmi ceux présents dans la table films.

    **Args**:\n
        user_data (User_data): Instance du modèle pydantic User_data

    **Returns**:\n
        json : Un json contenant des informations sur 5 films aléatoires.
            - movieId (int): Identifiant du film
            - title (str): Titre du film
            - genres (str): Genres du film séparés par des |
            - youtubeId (str): URL du trailer du film

    """    
    results = random_recos()
    logging.info('%s : Accès API GET /predict/rand_model',user_data.model_dump()["id"])
    results_json = results.to_json(orient="records")
    return results_json

@api.get("/predict/last_movies", tags=['Utilisateurs'], name="Sélection des 5 derniers films ajoutés")
async def pred_last_model(user_data: User_data):
    """
    Renvoie les 5 derniers films ajoutés en base.

    **Args**:\n
        user_data (User_data): Instance du modèle pydantic User_data

    **Returns**:\n
        json : Un json contenant des informations sur 5 films aléatoires.
            - movieId (int): Identifiant du film
            - title (str): Titre du film
            - genres (str): Genres du film séparés par des |
            - youtubeId (str): URL du trailer du film

    """    
    results = last_recos()
    logging.info('%s : Accès API GET /predict/last_movies',user_data.model_dump()["id"])
    results_json = results.to_json(orient="records")
    return results_json


class Watch_movie(BaseModel):
    userId: str
    movieId: int
    rating: Optional[int] = 3


@api.post("/user_activity", tags=['Utilisateurs'], name="Avis sur les films")
def user_activity(watched: Watch_movie):

    """
    Récupère l'activité d'un utilisateur lorsque celui-ci visionne un film ou lui attribue une note

    **Args**:\n
        watched (Watch_movie) : Instance du modèle pydantic Watch_movie

    **Does**:\n
        - dans le cas où l'utilisateur visionne un film, change la table Utilisateurs pour indiquer que c'est le dernier film visionné, et lui attribue une note par défaut de 3
        - dans le cas d'une notation, fait de même mais avec la note personnalisée

    **Returns**:\n
        json : indique si le film a été mis à jour ou ajouté
            - message
    
    **Examples**:\n
        - {"message": "Note MAJ"}
        - {"message": "Note ajoutee"}

    """    


    new_data = watched.model_dump()

    # Connexion à la base postgre
    conn = psycopg2.connect(
        dbname='dataflix',
        user='postgres',
        password='dataflix',
        host='data_container', 
        port='5432'
    )

    # Mise à jour du dernier film vu
    cur = conn.cursor()
    cur.execute("UPDATE utilisateurs SET last_viewed = %s WHERE userId = %s", (new_data['movieId'], new_data['userId'],))
    conn.commit()
    cur.close()
    
    # On vérifie si le film a déjà été noté par l'utilisateur 
    cur = conn.cursor()
    cur.execute("SELECT ratingId FROM notes where movieId = %s and userId = %s", (new_data['movieId'], new_data['userId'],))
    rows = cur.fetchone()
    cur.close()

    if rows is None: 
        cur = conn.cursor()
        cur.execute("INSERT INTO notes (userId, movieId, rating, timestamp_) VALUES (%s, %s, %s, %s)", 
                    (new_data['userId'],new_data['movieId'],new_data['rating'],time.time(),))
        conn.commit()
        cur.close()
        response = {"message": "Note ajoutee"}

    else :
        cur = conn.cursor()
        cur.execute("UPDATE notes SET rating = %s, timestamp_ = %s WHERE ratingId = %s", 
                    (new_data['rating'], time.time(), rows[0],))
        conn.commit()
        cur.close()
        conn.close()
        response = {"message": "Note MAJ"}


    return response



class CreateMovie(BaseModel):
    title: str
    genres : Optional[str] = ''
    youtubeId : Optional[str] = ''

@api.post("/create-movie", tags=['Admin'],name="Ajout d'un film en base")
def create_movie(movie_data: CreateMovie, user_rights: tuple = Depends(verify_admin)):
    """
    Ajoute ou met à jour un film en base.

    **Args**:\n
        - movie_data (CreateMovie): Instance du modèle pydantic CreateMovie
        - user_rights (tuple): tuple (name, role) dépendant de verify_admin  

    **Returns**:\n
        json : un message de confirmation

    **Raises**:\n
        HTTPException 401: Si l'utilisateur n'a pas les droits suffisants
    """

    username, role = user_rights
    new_movie = movie_data.model_dump()

    # Connexion à la base postgre
    conn = psycopg2.connect(
        dbname='dataflix',
        user='postgres',
        password='dataflix',
        host='data_container', 
        port='5432'
    )

    cur = conn.cursor()
    cur.execute("SELECT movieId FROM films where title=%s", (new_movie['title'],))
    rows = cur.fetchone()
    cur.close()

    if rows is None: 
        cur = conn.cursor()
        cur.execute("INSERT INTO films (title, genres, youtubeId) VALUES (%s, %s,%s)", 
                    (new_movie['title'], new_movie['genres'], new_movie['youtubeId'],))
        conn.commit()
        cur.close()
        response = {"message": "Film ajoute"}
        logging.info('%s : Accès API POST /create-movie : film "%s" créé', username, new_movie["title"] )


    else:
        cur = conn.cursor()
        cur.execute("UPDATE films SET genres = %s, youtubeId = %s WHERE movieId = %s", 
                    (new_movie['genres'], new_movie['youtubeId'], rows[0],))
        conn.commit()
        cur.close()
        conn.close()
        response = {"message": "Film mis a jour"}
        logging.info('%s : Accès API POST /create-movie : film "%s" mis à jour', username, new_movie["title"] )

    return response


@api.get("/train/train_cbf", tags=['Admin'], name="Entrainement du modèle")
async def train_cbf():
    """
    Entraîne le modèle CBF, à relancer à chaque fois qu'un film est ajouté.

    **Args**:\n
        Aucun argument à fournir

    **Does**:\n
        Effectue la Tf-Idf de la description et calcule la matrice de similarité cosinus entre ecteurs représentant les films, puis enregistre cette matrice.
    """

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
    df_films_new = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
    cur.close()
    conn.close()
    global df_films
    with df_films_lock:
        df_films = df_films_new


    train_CBF_model()
    
    global mat_sim
    with mat_sim_lock:
        mat_sim = load_CBF_similarity_matrix()

    logging.info('Modèle CBF entrainé')
    response = { "CBF model trained": "Done"}

    return response



@api.get("/predict/predict_CBF_model", tags=['Utilisateurs'], name="Sélection de 5 films recommandés par modèle CBF")
async def predict_CBF_model(user_data: User_data):
    """
    Effectue une prédiction de 5 films à partir du dernier film vu par l'utilisateur grâce à un modèle de filtrage par contenu

    **Args**:\n
        user_data (User_data): Instance du modèle pydantic User_data

    **Returns**:\n
        json : Un json contenant des informations sur 5 films recommandés par le modèle CBF.
            - movieId (int): Identifiant du film
            - title (str): Titre du film
            - genres (str): Genres du film séparés par des |
            - youtubeId (str): URL du trailer du film


        ou json: "Last viewed movie": "None" si l'utilisateur n'a pas encore vu de film

    """
    
    user = user_data.model_dump()
    userid = user["id"]

    conn = psycopg2.connect(
        dbname='dataflix',
        user='postgres',
        password='dataflix',
        host='data_container', 
        port='5432'
    )

    # Identification du dernier film vu
    cur = conn.cursor()
    cur.execute("SELECT t2.title FROM utilisateurs as t1 left join films as t2 on t1.last_viewed=t2.movieId WHERE t1.userId = %s and t1.last_viewed is not null", (userid,))
    req_title = cur.fetchone()
    cur.close()

    if req_title is not None:
        results = recommandations_CBF(df_films,req_title[0], mat_sim, 5)  

        logging.info('%s : Accès API GET /predict/predict_CBF_model', userid)
            
        results_json = results.to_json(orient="records")   

    else :
        results_json = json.dumps({"Last viewed movie": "None"})
        logging.info('%s : Accès API GET /predict/predict_CBF_model: No available prediction', userid)

    return results_json

if __name__ == '__main__':
    uvicorn.run(api, host='0.0.0.0', port=5000)

