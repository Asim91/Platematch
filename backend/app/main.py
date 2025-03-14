from fastapi import FastAPI
from app.api import app as api_app

app = FastAPI()

# Mount the API app at the root
app.mount("/", api_app)