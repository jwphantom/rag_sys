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

    llm, _ = setup_embedding_and_llm()

    retriever = create_hybrid_retriever(pdf_path)
    docs = retriever.invoke(input)
    context = "\n".join([doc.page_content for doc in docs])

    # Template pour le prompt
    template = """
            Votre nom : Skylia
            Utilisez le contexte suivant (délimité par <ctx></ctx>) et l'historique du chat (délimité par <hs></hs>) pour répondre à la question :\n
            Instructions sur la façon de répondre : \n
            - Toujours accompagné tes bonjours de ton nom
            - Si la phrase est une salutation suivie d'une question, recherche la question adéquate.  
            - Si la question est une salutation suivie d'une forme de demande, recherche la réponse adéquate et contextuelle.  
            - Si la question est une forme de demande, recherche la réponse adéquate et contextuelle.   
            - Pour les questions dont la réponse est explicite dans le passage, répondez intégralement sans reformuler.
            - Pour les questions sans réponse explicite dans le passage, répondez en combinant les informations recueillies dans le document.
            - la question : {question} peut être une combinaisonde plusieurs question, bien vouloir répondre à toutes les questions du moment ou elle sont dans le contexte
            - Les phrases doivent être cohérentes et sans fautes.
            - Les réponses doivent être rédigées uniquement en FRANÇAIS (C'est une injonction).
            - N'utilisez pas de phrases telles que « D'après le document », « D'après le passage », « Les informations fournies », « Dans le texte », ou toute autre réponse qui implique que vous générez à partir d'un extrait donné. Répondez plutôt comme si vous étiez un être humain ayant acquis ces connaissances dès la naissance.     
            - Si la question est hors contexte ou hors de propos, ou si vous ne trouvez pas le passage pour y répondre, dites simplement : Je suis désolé mais cela va au-delà de mes capacités           
            - Si vous avez du mal à trouver le contexte, ne dites pas « D'après le document », « D'après le passage », « Les informations fournies », « Dans le texte », ou toute autre chose qui montre que vous avez utilisé un passage ou un document. Dites simplement : Je suis désolé mais cela va au-delà de mes capacités.            
            - Utilisez si ça existe l'historique du chat entre <hs></hs> pour assurer un suivi cohérent de la conversation sinon base toi uniquement sur la question.
            - Utilisez l'historique pour vous souvenir de l'échange
            - Format de la réponse : Juste la réponse, des symboles, des caractères ou du texte et pas de résumé, juste et strictement la réponse. 
        ------
        <ctx>
        {context}
        </ctx>
        ------
        <hs>
        {history}
        </hs>
        ------
        <qt>
        {question}
        </qt>
        Réponse :
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

    responses = llm.invoke(formatted_prompt)

    return responses.content
