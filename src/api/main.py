from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
from pydantic import BaseModel
from passlib.context import CryptContext
import json
import csv
from pathlib import Path

api = FastAPI(
    title="Movie recomandation API",
    description="We will recomande the best movie for You",
    version="1.0.1")

security = HTTPBasic()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_admins_from_file(file_path):
    with open(file_path, "r") as file:
        admins = json.load(file)
    return admins

@api.get("/test")
def read_root():
    return {"message": "API is functional"}

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    admins = get_admins_from_file("admins.json")
    username = credentials.username
    password = credentials.password
    if not(admins.get(username)) or not(pwd_context.verify(password, admins[username]['hashed_password'])):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return username

@api.get("/secure-data/")
async def get_secure_data(username: str = Depends(verify_admin)):
    """
    Description:
    Cette route renvoie un message de bienvenue personnalisé en utilisant le nom d'utilisateur fourni en tant que dépendance.

    Args:
    - username (str, dépendance): Le nom d'utilisateur récupéré à partir de la dépendance `get_secure_data`.

    Returns:
    - str: Un message de bienvenue personnalisé avec le nom d'utilisateur.

    Raises:
    Aucune exception n'est levée explicitement, sauf si la dépendance `get_secure_data` échoue pour récupérer le nom d'utilisateur. Dans ce cas, une exception FastAPI sera levée automatiquement.
    """
    return {"message": f"Hello {username}, you have access to secure data"}

    
class CreateMovie(BaseModel):
    title: str
    genres : str = None

def get_next_id(file_path):
    with open(file_path, mode='r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        # Determine the maximum movieid
        max_movieid = max(int(row["movieId"]) for row in csv_reader)
    # Return the next available movieid
    return max_movieid + 1

@api.post("/create-movie/")
def create_movie(movie_data: CreateMovie, user: str = Depends(verify_admin)):
    file_path = "../../data/movies.csv"
    new_movie = movie_data.dict()
    new_movie["movieId"] = get_next_id(file_path)

    # à discuter
    with open(file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=new_movie.keys())
        csv_writer.writerow({'movieId': new_movie["movieId"] , 
                             'title': new_movie["title"] ,
                             'genres': new_movie["genres"] }
                            )

    return {"message": "movie created successfully", "movie": new_movie}

