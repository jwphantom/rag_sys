from fastapi import APIRouter
from app.schema.question import Question as SchemaQuestion

from app.utils.complex_input import generate_prompt


from dotenv import load_dotenv

load_dotenv(".env")

router = APIRouter()


@router.post("/generate-prompt")
async def chat(question: SchemaQuestion):

    path_pdf = "GUIDE_SOMMAIRE.pdf"

    response = generate_prompt(
        question.prompt, path_pdf, question.conversation, question.canal
    )

    return response


# Ajoutez cette partie pour gérer la route "/"
async def home(question: SchemaQuestion):
    return await chat(question)
