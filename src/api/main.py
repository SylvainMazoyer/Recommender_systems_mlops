from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn
from random_model import random_recos
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

# Configuration du logging
logging.basicConfig(filename='logs/API_log.log', encoding='utf-8', level=logging.INFO,
                    format='%(asctime)s : %(message)s', datefmt='%m/%d/%Y %H:%M:%S')


def wait_for_postgres(host, port, user, password, database, max_retries=10, retry_interval=5):
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
    title="Movie recommendation API",
    description="We will recommend the best movies for You",
    version="1.0.1")

@api.get("/")
def read_root():
    return {"message": "API is functional"}


  
""" Chargement des données nécessaires au lancement pour accélérer le processus par la suite:
    - Entraînement du modèle par content-based filtering
    - chargement de la matrice de similarité entre films ainsi générée

"""
train_CBF_model()
mat_sim = load_CBF_similarity_matrix()

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


security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



# Authentification admin simple
def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):

    """

    Mettre à jour :

    Vérifie les informations d'identification de l'administrateur.

    Args:
        credentials (HTTPBasicCredentials):
        Les informations d'identification HTTP de l'utilisateur.

    Returns:
        str: Le nom d'utilisateur de l'administrateur
        si les informations d'identification sont valides.

    Raises:
        HTTPException: Si les informations d'identification sont incorrectes,
        une exception HTTP 401 Unauthorized est levée.
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
            logging.info('%s : ERREUR 401 : Accès admin non autorisé', credentials.username)
            raise HTTPException(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Mot de passe incorrect",
                                headers={"WWW-Authenticate": "Basic"},
                            )

    # si le username n'est pas présent dans la table admin, on lève une erreur       
    else:
        logging.info('%s : ERREUR 401 : Accès admin non autorisé', credentials.username)

        raise HTTPException(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Utilisateur inconnu",
                                headers={"WWW-Authenticate": "Basic"},
                            )

    conn.close()
    return credentials.username, db_role



@api.get("/admin/{asked_role}")
async def get_secure_data(asked_role, user_rights: tuple = Depends(verify_admin)):
    """

    Mettre à jour

    Description:
    Cette route renvoie un message de bienvenue personnalisé en utilisant le nom d'utilisateur fourni en tant que dépendance.

    Args:
    - username (str, dépendance): Le nom d'utilisateur récupéré à partir de la dépendance `get_secure_data`.

    Returns:
    - str: Un message de bienvenue personnalisé avec le nom d'utilisateur.

    Raises:
    Aucune exception n'est levée explicitement, sauf si la dépendance
    `get_secure_data` échoue pour récupérer le nom d'utilisateur. 
    Dans ce cas, une exception FastAPI sera levée automatiquement.
    """
    username, role = user_rights

    if asked_role == 'Data' and role!='Data':
        logging.info('%s : ERREUR 401 : Accès admin non autorisé', username)
        raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Droits insuffisants",
                        headers={"WWW-Authenticate": "Basic"},
                    )
    logging.info('%s : Accès admin autorisé', username)
    return {"message": f"Hello {username}, you have access to secure data"}






class CreateUser(BaseModel):
    name: str


@api.post("/create-user")
def create_user(user_data: CreateUser):
    """
    Crée un nouvel utilisateur dans le système.

    Args:
        user_data (CreateUser): Les données de l'utilisateur à créer.
        user (str): Le nom d'utilisateur de l'administrateur.

    Does:
        Regarde si l'utilisateur est déjà dans la table utilisateurs
        - si il n'existe pas, ajout de ce dernier
        - si il existe on ne faire rien

    Returns:
        dict: 
        - Si le nom de l'utilisateur n'est pas dans la base d'utilisateurs,
        un message indiquant que l'utilisateur a été créé avec succès, 
        ainsi que les infos concernant l'utilisateur nouvellement créé.
        - Si le nom de l'utilisateur est dans la base d'utilisateurs,
        un message indiquant que l'utilisateur est déjà existant
        ainsi que les infos concernant l'utilisateur en question 

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

@api.get("/predict/rand_model")
async def pred_rand_model(user_data: User_data):
    """
    Renvoie 5 films aléatoires parmis ceux présents dans la table films

    Args:
        user_data (User_data):
        - name: str
        id: int

    Returns:
        json: 5 films aléatoires avec leur id, titre, leurs genres et leur trailer
        au format DataFrame jsonifié

    Raises:

    """    
    results = random_recos()
    logging.info('%s : Accès API GET /predict/rand_model',user_data.model_dump()["id"])
    results_json = results.to_json(orient="records")
    return results_json


class Watch_movie(BaseModel):
    userId: str
    movieId: int
    rating: Optional[int] = 3


@api.post("/user_activity")
def user_activity(watched: Watch_movie):

    """
    Récupère l'activité d'un utilisateur lorsque celui-ci visionne un film
    ou lui attribue une note

    Args:
        watched de la classe Watch_movie(BaseModel)
        - userId : str
        - movieId : int
        - rating, int optionnel fixé par défaut à 3

    Does:
        - dans le cas où l'utilisateur visionne un film, change la table Utilisateurs
        pour indiquer que c'est le dernier film visionné, et lui attribue une note de 3
        par defaut dans la table notes, qu'il aie déjà été noté ou non..
        - dans le cas d'une notation, fait de même mais avec la note personnalisée

    Returns:
        
        - si le film n'avait pas déjà été noté : 
        dict: "message": "Note ajoutee"
        - sinon dict: "message": "Note MAJ"

    Raises:

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

@api.post("/create-movie")
def create_movie(movie_data: CreateMovie, user_rights: tuple = Depends(verify_admin)):
    """
    Crée un nouveau film dans le système.

    Args:
        movie_data (CreateMovie): Les données du film à créer.
        user (str): Le nom d'utilisateur de l'administrateur.

    Does:
        - ajoute un film avec son titre et ses genres dans la table films

    Returns:
        dict: Un message indiquant que le film a été créé avec succès, 
        ainsi que les détails du film nouvellement créé.

    Raises:
        HTTPException: Si l'administrateur n'a pas les autorisations appropriées, 
        une exception HTTP 401 Unauthorized est levée.
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



  
@api.get("/train/train_cbf")
async def train_cbf():
    """
    Entraîne le modèle CBF, à relancer à chaque fois qu'un film est ajouté.

    Args:
        None

    Does:
        Effectue la Tf-Idf de la description et calcule la matrice de similarité 
        cosinus entre ecteurs représentant les films, puis enregistre cette matrice.

    Returns:
        None

    Raises:

    """    

    train_CBF_model()
    response = { "CBF model trained": "Done"}

    return response


@api.get("/train/load_CBF_sim_matrix")
async def load_CBF_sim_matrix():
    """
    Charge la matrice de similarité cosinus du CBF, à relancer à chaque fois qu'un film est ajouté et au lancement de l'api

    Args:
        None

    Does:
        cf ci-dessus

    Returns:
        dict: "Similarity matrix loaded": "Done"

    Raises:

    """    

    mat_sim = load_CBF_similarity_matrix()
    response = { "Similarity matrix loaded": "Done"}
    
    return response



# réécrire pour aller chercher les données dans la base et non dans les fichiers
@api.get("/predict/predict_CBF_model")
async def predict_CBF_model(user_data: User_data):
    """
    Effectue une prédiction de 5 films à partir du dernier film vu par l'utilisateur 
    si celui-ci était déjà présent en base et qu'il a déjà regardé un film. 
    La méthode employée est le filtrage par contenu.

    Args:
        user : nom de l'utilisateur pour lequel on veut faire la prédiction 

    Does:
        Regarde si l'utilisateur a déjà visionné un film au moins dans la table utilisateur
        Si oui; fait la prédiction du modèle CBF pour le dernier film vu l'utilisateur
        Sinon: indique que la prédiction n'est pas possible

    Returns:
        - si l'utilisateur a déjà visionné au moins un film:
        json: df des 5 films les plus similaires au dernier film vu par l'utilisateur
        dict: "Last viewed movie": "None" si l'utilisateur n'a pas encore vu de film

    Raises:

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
