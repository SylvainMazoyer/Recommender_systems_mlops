import csv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
from pydantic import BaseModel
from passlib.context import CryptContext
import json
import sys
sys.path.append('/home/ubuntu/projet/nov23_continu_mlops_recommandations')
from src.models.random_model import random_recos
from src.models.train_CBF_model import train_CBF_model
from src.models.load_CBF_similarity_matrix import load_CBF_similarity_matrix
from src.models.predict_CBF_model import recommandations_CBF
import logging 
import pandas as pd
import uvicorn
import time

logging.basicConfig(filename='src/api/API_log.log', encoding='utf-8', level=logging.INFO,
                    format='%(asctime)s : %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

api = FastAPI(
    title="Movie recommendation API",
    description="We will recommend the best movies for You",
    version="1.0.1")

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# chargement des données nécessaires au lancement pour accélérer le processus par la suite :
df_films = pd.read_csv("./data/films.csv")
mat_sim = load_CBF_similarity_matrix()
df_notes_launch = pd.read_csv("./data/notes.csv")
df_utilisateurs = pd.read_csv("./data/utilisateurs.csv")

def get_admins_from_file(file_path):
    with open(file_path, "r") as file:
        admins = json.load(file)
    return admins


@api.get("/")
def read_root():
    logging.info('Appel API GET /')
    return {"message": "API is functional"}


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
    admins = get_admins_from_file("admins.json")

    username = credentials.username
    password = credentials.password
    if not (admins.get(username)) or not (pwd_context.verify(password, pwd_context.hash(admins.get(username).get('password')))):
        logging.info('%s : ERREUR 401 : Accès admin non autorisé', username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return username

@api.get("/admin")
async def get_secure_data(username: str = Depends(verify_admin)):
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
    logging.info('%s : Accès admin autorisé', username)
    return {"message": f"Hello {username}, you have access to secure data"}


# Authentification admin datascientist
def verify_equipe_ds(username: str = Depends(verify_admin)):
    """
    Vérifie que l'utilisateur est membre de l'équipe de data science.

    Args:
        username (str): Le nom d'utilisateur.

    Returns:
        str: Le nom d'utilisateur de l'administrateur si celui-ci est membre de l'équipe de data science.

    Raises:
        HTTPException: Si l'administrateur n'est pas membre de l'équipe de data science, 
        une exception HTTP 403 Forbidden est levée.
    """
    admins = get_admins_from_file("admins.json")
    if admins.get(username).get("role") != "equipe_ds":
        logging.info('%s : ERREUR 403 : Accès datascientist non autorisé', username)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return username

@api.get("/equipe_ds")
async def secure_data_equipe_ds(username: str = Depends(verify_equipe_ds)):
    logging.info('%s : Accès datascientist autorisé', username)
    return {"message": f"Hello {username}, you have access to secure data"}

def get_next_id(file_path, columnid):
    with open(file_path, mode='r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        # Determine the maximum movieid
        max_id = max(int(row[columnid]) for row in csv_reader)
    # Return the next available movieid
    return max_id + 1


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

    if len(df_utilisateurs[df_utilisateurs['name'] == new_user['name']]) == 0: 
        response = {"message": "user created successfully", "user": new_user}
        logging.info('%s : Accès API POST /create-user : user créé', new_user["name"])
    else :
        response = {"message": "user already exists", "user": new_user}
        logging.info('%s : Accès API POST /create-user : user déjà existant', new_user["name"])

    return response



class CreateMovie(BaseModel):
    title: str
    genres : Optional[str] = None

@api.post("/create-movie")
def create_movie(movie_data: CreateMovie, user: str = Depends(verify_admin)):
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
    file_path = "./data/films.csv"
    response = {}

    new_movie = movie_data.model_dump()
        
    # Cas où le film existe déjà
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if new_movie["title"] == row['title']:
                response = {"message": "movie already exists", "movie": new_movie}
                logging.info('%s : Accès API POST /create-movie : film "%s" déjà existant', user, new_movie["title"] )

    if response == {}:
        new_movie["movieId"] = get_next_id(file_path, 'movieId')

        with open(file_path, mode='a', newline='', encoding='utf-8') as csv_file:
                
            csv_writer = csv.DictWriter(csv_file, fieldnames = ['movieId', 'title', 'genres'])
            csv_writer.writerow({'movieId': new_movie["movieId"] , 
                                    'title': new_movie["title"] ,
                                    'genres': new_movie["genres"] }
                                    )
            response = {"message": "movie created successfully", "movie": new_movie}
            logging.info('%s : Accès API POST /create-movie : film "%s" créé', user, new_movie["title"] )

    return response



@api.get("/predict/rand_model")
async def pred_rand_model(user_data: CreateUser):
    """
    Renvoie 5 films aléatoires

    Args:
        None

    Returns:
        json: 5 films aléatoires avec leur id, leur genre et leur trailer

    Raises:

    """    
    results = random_recos()
    logging.info('%s : Accès API GET /predict/rand_model : %s', 
                 user_data.model_dump()["name"], results[["movieId", 'title']].to_json(orient="records"))
    results_json = results.to_json(orient="records")

    return results_json


@api.get("/train/train_cbf")
async def train_cbf():
    """
    Entraîne le modèle CBF, à relancer à chaque fois qu'un film est ajouté

    Args:
        None

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

    Returns:
        None

    Raises:

    """    

    mat_sim = load_CBF_similarity_matrix()
    response = { "Similarity matrix loaded": "Done"}
    
    return response



@api.get("/predict/predict_CBF_model")
async def predict_CBF_model(user_data: CreateUser):
    """
    Effectue une prédiction de 5 films à partir du dernier film vu par l'utilisateur si celui-ci était déjà présent en base,
    et qu'il a déjà regardé un film. La méthode employé est le filtrage par contenu.

    Args:
        user : nom de l'utilisateur pour lequel on veut faire la prédiction 

    Returns:
        df des 5 films les plus similaires au dernier film vu par l'utilisateur

    Raises:

    """
    
    user = user_data.model_dump()
    username = user["name"]

    df_user = df_utilisateurs[df_utilisateurs["name"] == username]

    if len(df_user) != 0:
        if df_user["last_viewed"].iloc[0] == "None":
            results_json = json.dumps({"Last viewed movie": "None"})
            logging.info('%s : Accès API GET /predict/predict_CBF_model: No avalaible prediction', username)

        else:
            last_viewed = int(df_utilisateurs[df_utilisateurs["name"] == username]["last_viewed"].iloc[0])
            title = df_films[df_films["movieId"] == last_viewed]["title"].iloc[0]

            results = recommandations_CBF(df_films, title, mat_sim, 5)  

            logging.info('Accès API GET /predict/predict_CBF_model : %s', 
                        results[["movieId", 'title']].to_json(orient="records"))
            
            results_json = results.to_json(orient="records")                
    else:
        results_json = json.dumps({"Last viewed movie": "None"})
        logging.info('Accès API GET /predict/predict_CBF_model: No avalaible prediction')

    return results_json


class Watch_movie(BaseModel):
    userId: int
    movieId: int
    rating: Optional[int] = 3

@api.post("/user_activity")
def user_activity(watched: Watch_movie):
    """ récupère l'activité d'un utilisateur lorsque celui-ci regarde un film dans le streamlit
    - met à jour à jour la table utilisateurs avec l'id du film en question comme dernier film regardé
    - met à jour la table notes avec une note de 3 par défaut pour le film regardé
    - dans le cas de la notation d'un film, fait de même dans la table note avec la note choisie"""

    df_notes = df_notes_launch.copy()

    df_utilisateurs[df_utilisateurs["UserId"]==watched.userId] = watched.movieId

    timestamp = time.time()

    d = {'userId': [watched.userId], 'movieId': [watched.movieId], 'rating':[watched.rating], "timestamp":[timestamp]}
    df_note = pd.dataframe(data=d)

    df_notes = pd.concat([df_notes, df_note], ignore_index=True)

    df_utilisateurs.to_csv("./data/utilisateurs.csv", index=False)
    df_notes.to_csv("./data/notes.csv", index=False)

    return "Note added to base"


if __name__ == "__main__":
    uvicorn.run("main:api", host="127.0.0.1", port=8000, log_level="info")

