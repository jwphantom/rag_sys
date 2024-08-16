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

    if llm is None:
        logger.error("Le modèle LLM n'est pas correctement configuré.")
        return "Je suis désolé, il y a eu une erreur dans la configuration du modèle."

    logger.info("llm passée")

    logger.info("retrieve avant")

    retriever = create_hybrid_retriever(pdf_path)

    if retriever is None:
        logger.error("Échec de la création du hybrid retriever.")
        return (
            "Je suis désolé, je n'ai pas pu initialiser le récupérateur de documents."
        )

    logger.info("retrieve passée")

    docs = retriever.invoke(input)

    if docs is None or len(docs) == 0:
        logger.error("Aucun document trouvé par le retriever.")
        return "Je suis désolé, je n'ai pas pu trouver d'informations pertinentes."

    logger.info("docs passée")

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

    logger.info(f"prompt passée")

    # Générer le prompt formaté
    formatted_prompt = prompt.format(history=history, context=context, question=input)

    logger.info(f"Formatted prompt: \n{formatted_prompt}")
    logger.info(f"formatted prompt passée ")

    try:
        responses = llm.invoke(formatted_prompt)
    except Exception as e:
        logger.error(f"Erreur lors de l'invocation du modèle : {str(e)}")
        return "Je suis désolé, il y a eu une erreur dans la génération de la réponse."

    if responses is not None:
        logger.info("réponses généré ")
        logger.info(f"reponses passée \n {responses}")
    else:
        logger.error("Le modèle n'a pas généré de réponse.")

    return (
        responses.content
        if responses is not None
        else "Je suis désolé, je n'ai pas pu générer de réponse."
    )
