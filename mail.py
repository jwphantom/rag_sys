import asyncio
import aiohttp
from aioimaplib import aioimaplib
import logging
from datetime import datetime
import email
from app.utils.mail.content import decode_mime_words
from app.utils.mail.reply import reply_mail
from app.utils.handle_input.handle_input import handle_input
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

username = os.getenv("USERNAME")
tenant_id = os.getenv("TOKEN_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
refresh_token = os.getenv("REFRESH_TOKEN")
smtp_password = os.getenv("SMTP_PASSWORD")
token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"


async def get_access_token():
    async with aiohttp.ClientSession() as session:
        data = {
            "client_id": client_id,
            "scope": "https://outlook.office365.com/.default",
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "client_secret": client_secret,
        }
        async with session.post(token_url, data=data) as response:
            if response.status == 200:
                tokens = await response.json()
                return tokens["access_token"]
            else:
                logger.error(f"Error: {response.status}")
                logger.error(await response.json())
                return None


async def mail_job():
    while True:
        try:
            access_token = await get_access_token()
            if not access_token:
                await asyncio.sleep(60)
                continue

            imap_client = aioimaplib.IMAP4_SSL("outlook.office365.com")
            await imap_client.wait_hello_from_server()
            await imap_client.login(username, access_token)
            await imap_client.select("INBOX")

            today = datetime.now().strftime("%d-%b-%Y")
            _, messages = await imap_client.search(f'(SINCE "{today}" UNSEEN)')

            for num in messages[0].split():
                _, msg_data = await imap_client.fetch(num, "(RFC822)")
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)

                from_address = email_message["From"]
                if "olongowilliam@gmail.com" in from_address:
                    subject = decode_mime_words(
                        email_message["Subject"] or "Pas de sujet"
                    )
                    logger.info(f"De : {from_address}")
                    logger.info(f"Sujet : {subject}")
                    logger.info(f"Date : {email_message['Date']}")

                    result = await handle_input(email_message)

                    reply_body = f"{result['response']}\n{result['history']}"

                    await reply_mail(
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

                    await imap_client.store(num, "+FLAGS", "\\Seen")
                else:
                    logger.debug(f"Email ignoré : {from_address}")

            await imap_client.logout()
            await asyncio.sleep(10)

        except asyncio.CancelledError:
            logger.info("Tâche mail_job annulée")
            break
        except Exception as e:
            logger.error(f"Erreur dans mail_job: {str(e)}")
            await asyncio.sleep(60)
