from fastapi import FastAPI
from app.api import chat
from fastapi.middleware.cors import CORSMiddleware
from app.schema.question import Question as SchemaQuestion
import os
from dotenv import load_dotenv
import asyncio
from mail import main as mail_job

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

# Inclusion du router
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])


# @app.on_event("startup")
# async def start_background_task():
#     asyncio.create_task(mail_job())


@app.get("/")
async def read_root():
    return {"message": "Welcome to the API"}


@app.get("/home")
async def read_root():
    return {"message": "Welcome to the API"}


@app.post("/")
async def home(question: SchemaQuestion):
    return await chat.home(question)
