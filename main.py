from fastapi import FastAPI
from app.api import chat
from fastapi.middleware.cors import CORSMiddleware
from app.schema.question import Question as SchemaQuestion
import os
from dotenv import load_dotenv
import asyncio
from contextlib import asynccontextmanager
from mail import (
    mail_job,
)  # Assurez-vous que ce fichier existe avec la fonction mail_job

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Démarrage
    mail_task = asyncio.create_task(mail_job())
    yield
    # Nettoyage
    mail_task.cancel()
    try:
        await mail_task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permet tous les origines pour le développement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion du router
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])


@app.get("/")
async def read_root():
    return {"message": "Welcome to the API"}


@app.get("/home")
async def read_home():
    return {"message": "Welcome to the API"}


@app.post("/")
async def home(question: SchemaQuestion):
    return await chat.home(question)
