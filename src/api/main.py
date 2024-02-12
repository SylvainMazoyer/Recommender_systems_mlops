from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
from pydantic import BaseModel

api = FastAPI(
    title="Movie recomandation API",
    description="We will recomande the best movie for You",
    version="1.0.1")

security = HTTPBasic()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



@api.get("/test")
def read_root():
    return {"message": "API is functional"}

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    user = credentials.username
    password = credentials.password
    if user != "admin" and password != "4dm1N" :        
        raise HTTPException(status_code=401, 
                            detail=f"not admin credentials {user}: {password}")
    return user

@api.get("/secure-data/")
async def get_secure_data(user: str = Depends(verify_admin)):
    return {"message": f"Hello {user}, you have access to secure data"}

    
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