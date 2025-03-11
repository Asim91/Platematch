from fastapi import FastAPI
from app.api import app as api_app

app = FastAPI()

app.mount("/", api_app)