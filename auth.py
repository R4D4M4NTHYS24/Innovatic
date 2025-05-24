# auth.py
import os
import logging
from dotenv import load_dotenv
from msal import ConfidentialClientApplication

# Carga las variables de .env
load_dotenv()

CLIENT_ID     = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID     = os.getenv("TENANT_ID")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_graph_token():
    """
    Obtiene un token OAuth2 para Microsoft Graph.
    """
    app = ConfidentialClientApplication(
        client_id=CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET,
    )
    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )
    if "access_token" in result:
        logger.info("Token obtenido correctamente.")
        return result["access_token"]
    else:
        logger.error("Error obteniendo token: %s", result.get("error_description"))
        return None

if __name__ == "__main__":
    token = get_graph_token()
    if token:
        print("Token válido — primeros 100 caracteres:\n", token[:100])
