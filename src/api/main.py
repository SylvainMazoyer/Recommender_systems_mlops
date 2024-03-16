from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn
from random_model import random_recos
from pydantic import BaseModel
import pandas as pd
import psycopg2
from typing import Optional
from passlib.context import CryptContext
import time
import logging 

# Configuration du logging
logging.basicConfig(filename='logs/API_log.log', encoding='utf-8', level=logging.INFO,
                    format='%(asctime)s : %(message)s', datefmt='%m/%d/%Y %H:%M:%S')


api = FastAPI(
    title="Movie recommendation API",
    description="We will recommend the best movies for You",
    version="1.0.1")

@api.get("/")
def read_root():
    return {"message": "API is functional"}



security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



# Authentification admin simple
def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):

    """
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

    Returns:
        dict: Un message indiquant que l'utilisateur a été créé avec succès, 
        ainsi que les détails de l'utilisateur nouvellement créé.

    Raises:
        HTTPException: Si l'administrateur n'a pas les autorisations appropriées,
        une exception HTTP 401 Unauthorized est levée.
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


@api.get("/predict/rand_model")
async def pred_rand_model():
    """
    Renvoie 5 films aléatoires

    Args:
        None

    Returns:
        json: 5 films aléatoires avec leur id, leur genre et leur trailer

    Raises:

    """    
    results = random_recos()
    logging.info('Accès API GET /predict/rand_model : %s')
    results_json = results.to_json(orient="records")
    return results_json


class Watch_movie(BaseModel):
    userId: str
    movieId: int
    rating: Optional[int] = 3


@api.post("/user_activity")
def user_activity(watched: Watch_movie):
    """ récupère l'activité d'un utilisateur lorsque celui-ci clique sur le trailer d'un film 
    - met à jour à jour la table utilisateurs avec l'id du film en question comme dernier film regardé
    - met à jour la table notes avec une note de 3 pour le film regardé"""

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



if __name__ == '__main__':
    uvicorn.run(api, host='0.0.0.0', port=5000)

