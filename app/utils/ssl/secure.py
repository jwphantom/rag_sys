import ssl
import logging
from imapclient import IMAPClient
import certifi
from typing import Optional


class SecureIMAPConnection:
    def __init__(
        self,
        host: str,
        username: str,
        ssl_context: Optional[ssl.SSLContext] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.host = host
        self.username = username
        self.logger = logger or logging.getLogger(__name__)
        self.ssl_context = ssl_context or self._create_default_ssl_context()
        self.client = None

    def _create_default_ssl_context(self) -> ssl.SSLContext:
        """Crée un contexte SSL sécurisé avec les certificats du système"""
        context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH, cafile=certifi.where()
        )
        # Options de sécurité recommandées
        context.options |= (
            ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        )  # Désactive TLS 1.0 et 1.1
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        return context

    def connect(self, access_token: str) -> IMAPClient:
        """Établit une connexion IMAP sécurisée"""
        try:
            self.client = IMAPClient(
                host=self.host, ssl_context=self.ssl_context, use_uid=True
            )
            self.client.oauth2_login(self.username, access_token)
            self.logger.info(f"Connexion sécurisée établie avec {self.host}")
            return self.client

        except ssl.SSLCertVerificationError as e:
            self.logger.error(f"Erreur de vérification du certificat SSL: {str(e)}")
            self.logger.info("Tentative de résolution avec les certificats système...")
            # Tentative avec les certificats système
            self.ssl_context.load_default_certs()
            return self.connect(access_token)

        except Exception as e:
            self.logger.error(f"Erreur de connexion IMAP: {str(e)}")
            raise

    def disconnect(self):
        """Ferme la connexion de manière sécurisée"""
        if self.client:
            try:
                self.client.logout()
                self.logger.info("Déconnexion réussie")
            except Exception as e:
                self.logger.error(f"Erreur lors de la déconnexion: {str(e)}")
            finally:
                self.client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
