import os
import requests
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_access_token(tenant_id, client_id, client_secret, refresh_token):

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

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
