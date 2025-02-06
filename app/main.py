from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(title="Freelance Platform API", version="1.0.0")


@app.get("/")
def root():
    return {"message": "Wellcome to IP-lance"}

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("LOCALHOST"))

