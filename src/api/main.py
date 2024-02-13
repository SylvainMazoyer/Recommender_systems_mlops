from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
from pydantic import BaseModel
from passlib.context import CryptContext
import json


api = FastAPI(
    title="Movie recomandation API",
    description="We will recomande the best movie for You",
    version="1.0.1")

security = HTTPBasic()


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
    genres : Optional[list] = None


@api.post("/create-movie/")
def create_movie(movie_data: CreateMovie, user: str = Depends(verify_admin)):
    new_movie = movie_data.dict()
    # à discuter
    '''with open("data/movies.csv", mode='a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=new_movie.keys())
        csv_writer.writerow(new_movie)'''

    return {"message": "movie created successfully", "movie": new_movie}