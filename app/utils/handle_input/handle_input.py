from app.api.chat import chat
from app.utils.handle_input.confirmation_informations import (
    handle_response_confirmation_informations,
)
from app.utils.handle_input.conversation_ending import handle_conversation_ending
from app.utils.handle_input.greeting_how_are_you import handle_greeting_and_how_are_you
from app.utils.handle_input.handle_string import parse_string_to_list_of_dicts
from app.utils.mail.content import clean_and_format_content

from app.schema.question import Question as SchemaQuestion

import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_input(content):
    new_request, history, parts = clean_and_format_content(content)

    question = SchemaQuestion(canal="email", prompt=new_request, conversation=history)

    response = ""
    mail = False

    if len(parts) < 2:
        if handle_greeting_and_how_are_you(new_request):
            logger.info("Avant l'appel à reponse greeting < 2")
            response = handle_greeting_and_how_are_you(new_request)
            logger.info("Après l'appel à reponse greeting < 2")
            mail = True

        if handle_response_confirmation_informations(new_request):
            response = "Stop"

        elif handle_conversation_ending(new_request):
            response = "Stop"

        else:
            mail = True
            logger.info("Avant l'appel à reponse chat < 2")
            response = await chat(question)
            logger.info("Avant l'appel à reponse chat < 2")

    else:

        parse_old_chat = parse_string_to_list_of_dicts(history)

        print(parse_old_chat)

        if parse_old_chat[0] <= 2:
            if parse_old_chat[0]["Skylia"]:
                if parse_old_chat["Skylia"].startswith(
                    "Récapulatifs de vos informations"
                ):
                    response = handle_greeting_and_how_are_you(parse_old_chat["User"])
                    if not response:
                        if handle_response_confirmation_informations(
                            parse_old_chat["User"]
                        ):
                            mail = True

                            response = "Merci pour la confirmation, vous serez contacté dans les prochains jours."
                        else:

                            mail = True
                            response = await chat(question)
            else:
                response = handle_greeting_and_how_are_you(parse_old_chat["User"])
                if not response:
                    mail = True
                    response = await chat(question)

        else:
            if handle_greeting_and_how_are_you(new_request):
                response = "Stop"

            elif handle_response_confirmation_informations(new_request):
                response = "Stop"

            elif handle_conversation_ending(new_request):
                response = "Stop"

            else:
                mail = True
                response = await chat(question)

    return {
        "history": history,
        "new_request": new_request,
        "response": response,
        "mail": mail,
    }
