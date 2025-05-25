# auth.py
import os
import logging
from dotenv import load_dotenv
from msal import PublicClientApplication, SerializableTokenCache

load_dotenv()
logger = logging.getLogger(__name__)

CLIENT_ID   = os.getenv("CLIENT_ID")
TENANT_ID   = os.getenv("TENANT_ID")
SCOPES      = ["User.Read", "Mail.Read", "Mail.Send"]
CACHE_PATH  = "token_cache.bin"

# Prepara el cache
token_cache = SerializableTokenCache()
if os.path.exists(CACHE_PATH):
    token_cache.deserialize(open(CACHE_PATH, "r").read())

# Crea la app con el cache
app = PublicClientApplication(
    client_id=CLIENT_ID,
    authority=f"https://login.microsoftonline.com/common",
    token_cache=token_cache,
)

def get_graph_token() -> str | None:
    # 1) Intenta silent
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            logger.debug("Token silent obtenido de cache")
            return result["access_token"]

    # 2) Si no hay token, inicia Device Code Flow UNA VEZ
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        logger.error("Error iniciando Device Code Flow: %s", flow)
        return None
    print(flow["message"])  # "Ve a ... e ingresa este código..."

    result = app.acquire_token_by_device_flow(flow)
    if "access_token" in result:
        # Guarda cache en disco
        with open(CACHE_PATH, "w") as f:
            f.write(token_cache.serialize())
        logger.info("Token delegado obtenido y cache guardado.")
        return result["access_token"]

    logger.error("Error obteniendo token: %s", result.get("error_description"))
    return None
