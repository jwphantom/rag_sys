import base64
import smtplib
import ssl
import time
from tokenize import TokenError
import requests
from imapclient import IMAPClient
import logging
from datetime import datetime, timedelta
import email

import email.utils

import os


from app.utils.mail.content import (
    decode_mime_words,
)
from app.utils.mail.reply import reply_mail
from app.utils.handle_input.handle_input import handle_input

import asyncio

username = os.getenv("USERNAME")
tenant_id = os.getenv("TOKEN_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
refresh_token = os.getenv("REFRESH_TOKEN")
smtp_password = os.getenv("SMTP_PASSWORD")
token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"


# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


allowed_domains = ["yahoo.com", "icloud.com", "hotmail.com", "gmail.com"]


def get_access_token():

    data = {
        "client_id": client_id,
        "scope": "https://outlook.office365.com/.default",
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "client_secret": client_secret,
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        tokens = response.json()
        return tokens["access_token"]
    else:
        logger.error(f"Error: {response.status_code}")
        logger.error(response.json())
        exit(1)


async def main():

    access_token = get_access_token()

    # Paramètres IMAP
    IMAP_SERVER = "outlook.office365.com"

    try:
        with IMAPClient(IMAP_SERVER, ssl=True) as client:
            client.oauth2_login(username, access_token)
            logger.info("Connexion réussie!")

            client.select_folder("INBOX")

            # Obtenir la date d'aujourd'hui à minuit
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_str = today.strftime("%d-%b-%Y")

            while True:
                # Rechercher les emails de la journée
                search_criteria = ["SINCE", today_str, "UNSEEN"]
                messages = client.search(search_criteria)

                # Trier les messages du plus récent au plus ancien
                messages.sort(reverse=True)

                # Afficher les messages de la journée
                for msg_id in messages:
                    msg_data = client.fetch([msg_id], ["ENVELOPE", "RFC822"])
                    envelope = msg_data[msg_id][b"ENVELOPE"]
                    email_message = email.message_from_bytes(
                        msg_data[msg_id][b"RFC822"]
                    )

                    from_address = (
                        envelope.from_[0].mailbox.decode()
                        + "@"
                        + envelope.from_[0].host.decode()
                    )

                    if from_address == "olongowilliam@gmail.com":
                        subject = decode_mime_words(
                            envelope.subject.decode()
                            if envelope.subject
                            else "Pas de sujet"
                        )
                        logger.info(f"De : {envelope.from_[0].name} <{from_address}>")
                        logger.info(f"Sujet : {subject}")
                        logger.info(f"Date : {envelope.date}")

                        result = await handle_input(email_message)

                        # Prepare the reply body
                        reply_body = f"{result['response']}\n"
                        reply_body += result["history"]

                        # Send the reply
                        reply_mail(
                            username,
                            smtp_password,
                            from_address,
                            subject,
                            email_message["Message-ID"],
                            email_message["References"],
                            reply_body,
                        )

                        logger.info(f"Reply: \n {result['response']} ")
                        logger.info("=" * 40)

                        client.add_flags([msg_id], [r"\Seen"])
                    else:
                        logger.debug(f"Email ignoré : {from_address}")

                time.sleep(10)

    except Exception as e:
        logger.error(f"Erreur détaillée: {str(e)}")
