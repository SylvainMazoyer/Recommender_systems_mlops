from fastapi import FastAPI
import uvicorn
from random_model import random_recos

api = FastAPI(
    title="Movie recommendation API",
    description="We will recommend the best movies for You",
    version="1.0.1")

@api.get("/")
def read_root():
    return {"message": "API is functional"}

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
    results_json = results.to_json(orient="records")
    return results_json

if __name__ == '__main__':
    uvicorn.run(api, host='0.0.0.0', port=5000)

