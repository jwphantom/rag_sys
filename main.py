from fastapi import FastAPI
from app.api import (
    chat,
    evaluation,
    evaluation_config1,
    evaluation_config2,
    evaluation_config3,
    evaluation_config4,
)
from fastapi.middleware.cors import CORSMiddleware
from app.schema.question import Question as SchemaQuestion
import os
from dotenv import load_dotenv
import asyncio
from mail import main as mail_job

load_dotenv()

origins = [
    "http://localhost:3000",
]

app = FastAPI()

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["evaluation"])
app.include_router(
    evaluation_config1.router,
    prefix="/api/evaluation-config1",
    tags=["evaluation_config1"],
)
app.include_router(
    evaluation_config2.router,
    prefix="/api/evaluation-config2",
    tags=["evaluation_config2"],
)
app.include_router(
    evaluation_config3.router,
    prefix="/api/evaluation-config3",
    tags=["evaluation_config3"],
)
app.include_router(
    evaluation_config4.router,
    prefix="/api/evaluation-config4",
    tags=["evaluation_config4"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def start_background_task():
    asyncio.create_task(mail_job())  # Lancer le job en arrière-plan


@app.get("/")
async def read_root():
    return {"message": "Welcome to the API"}


@app.post("/")
async def home(question: SchemaQuestion):
    return await chat.home(question)
