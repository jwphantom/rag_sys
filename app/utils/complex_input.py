from langchain_community.vectorstores import Chroma
from app.utils.llama3RAG import (
    create_retriever,
    load_and_split_document,
    setup_embedding_and_llm,
    create_hybrid_retriever,
)

from langchain.prompts import PromptTemplate

import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_prompt(input, pdf_path, history, canal):

    logger.info("llm avant")

    llm, _ = setup_embedding_and_llm()

    retriever = create_hybrid_retriever(pdf_path)

    docs = retriever.invoke(input)

    context = "\n".join([doc.page_content for doc in docs])

    # Template pour le prompt
    template = """
            Votre nom : Skylia
            Utilisez le contexte suivant (délimité par <ctx></ctx>) et l'historique du chat (délimité par <hs></hs>) pour répondre à la question :\n
            ...
        """

    if canal == "email":
        template += """
        Réponses améliorées
        Essaie de comprendre le texte dans le contenu historique entre <hs></hs> qui provient des conversations par courriel de l'utilisateur afin de répondre de manière cohérente.
        """

    prompt = PromptTemplate(
        input_variables=["history", "context", "question"],
        template=template,
    )

    # Générer le prompt formaté
    formatted_prompt = prompt.format(history=history, context=context, question=input)

    logger.info("avant llm")
    responses = llm.generate_prompt(formatted_prompt)

    logger.info("après llm")

    return responses.content
