from fastapi import FastAPI

api = FastAPI(
    title="Movie recomandation API",
    description="We will recomande the best movie for You",
    version="1.0.1")

@api.get("/test")
def read_root():
    return {"message": "API is functional"}
