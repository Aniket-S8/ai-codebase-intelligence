from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "AI Codebase Intelligence System is running 🚀"}