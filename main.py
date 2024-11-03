import logging
from fastapi import FastAPI
from app.api import chat
from fastapi.middleware.cors import CORSMiddleware
from app.schema.question import Question as SchemaQuestion
import os
from dotenv import load_dotenv
import asyncio
from mail import mail_job

from contextlib import asynccontextmanager
import asyncio

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permet tous les origines pour le développement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utilisation de l'événement lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code à exécuter au démarrage
    logger.info("Démarrage de mail_job")
    task = asyncio.create_task(mail_job())
    yield
    # Code à exécuter à la fermeture
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the API"}


@app.get("/home")
async def read_root():
    return {"message": "Welcome to the API"}


@app.post("/")
async def home(question: SchemaQuestion):
    return await chat.home(question)


# Inclusion du router
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
