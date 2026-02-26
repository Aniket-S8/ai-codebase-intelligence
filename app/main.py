from fastapi import FastAPI
from sqlalchemy import text
from app.database import engine
from app import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Phase 1 DB Models Created 🚀"}