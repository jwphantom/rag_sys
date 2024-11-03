import base64
import smtplib
import ssl
import time
import requests
from app.utils.ssl.secure import SecureIMAPConnection
from imapclient import IMAPClient
import logging
from datetime import datetime, timedelta
import email

import email.utils

import os


from app.utils.mail.content import (
    decode_mime_words,
)
from app.utils.mail.token import get_access_token
from app.utils.mail.reply import reply_mail
from app.utils.handle_input.handle_input import handle_input

import asyncio

username = os.getenv("USERNAME")
tenant_id = os.getenv("TOKEN_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("AZURE_SECRET")
refresh_token = os.getenv("REFRESH_TOKEN")
smtp_password = os.getenv("SMTP_PASSWORD")


# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


allowed_domains = ["yahoo.com", "icloud.com", "hotmail.com", "gmail.com"]


# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

allowed_domains = ["yahoo.com", "icloud.com", "hotmail.com", "gmail.com"]


async def mail_job():
    access_token = get_access_token(tenant_id, client_id, client_secret, refresh_token)

    # Paramètres IMAP
    IMAP_SERVER = "outlook.office365.com"

    imap_connection = SecureIMAPConnection(
        host="outlook.office365.com", username=username, logger=logger
    )

    try:
        with imap_connection.connect(access_token) as client:
            logger.info(f"Connexion réussie à la boite mail {username}")
            logger.info("=" * 40)

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

                if not messages:
                    logger.debug("Aucun nouveau message trouvé")
                else:
                    print("fff")
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
                        if (result["response"] != "Stop") or (
                            result["response"] != "ENDCONV"
                        ):
                            reply_mail(
                                username,
                                smtp_password,
                                from_address,
                                subject,
                                email_message["Message-ID"],
                                email_message["References"],
                                reply_body,
                            )
                        logger.info("=" * 40)
                        logger.info(f"Requête USER: \n {result['new_request']} ")
                        logger.info("=" * 40)
                        logger.info(f"Réponse IA: \n {result['response']} ")
                        logger.info("=" * 40)

                        client.add_flags([msg_id], [r"\Seen"])

                await asyncio.sleep(10)

    except Exception as e:
        logger.error(f"Erreur détaillée: {str(e)}")
