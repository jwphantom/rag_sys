import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import smtplib

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reply_mail(
    username, smtp_password, to_email, subject, message_id, references, body
):
    reply = MIMEMultipart()
    reply["Subject"] = f"Re: {subject}"
    reply["From"] = username
    reply["To"] = to_email
    reply["In-Reply-To"] = message_id
    reply["References"] = references

    # Add the response body to the email
    reply.attach(MIMEText(body, "plain"))

    # Configuration du serveur SMTP
    smtp_server = "smtp.office365.com"
    smtp_port = 587

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, smtp_password)
            server.send_message(reply)
        logger.info(f"Email de remerciement envoyé à {to_email}")
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email : {str(e)}")
